#!/usr/bin/env python3
"""
build_galaxy.py — the file graph as an audit instrument.

Imports scan_files() from build_graph.py so there is exactly one definition
of what an edge is. Adds two things that neither earlier renderer had:

  1. DEFECT DETECTION. The graph flags real anomalies in place, in the
     structure where they live, instead of being a picture you admire.
     Detected: whitespace in a path component, notes matching neither
     naming convention (invisible to make_index.py), note numbers claimed
     by more than one file, notes with no Status label, zero-byte files.

  2. AGE. One git pass reads last-commit time per file. Recent work glows
     hot, dormant files cool. Degrades silently if git is unavailable.

Rendering: two-pass bloom on canvas 2D. A half-resolution glow buffer is
composited back with additive blending, which is how you get real bloom
without WebGL. Still zero dependencies, no CDN, no backdrop-filter.

  python scripts/build_galaxy.py            # writes galaxy.html
  python scripts/build_galaxy.py --selftest # anti-vacuity gate
"""

import argparse
import collections
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_graph import scan_files, NUM_RE, STATUS_RE  # noqa: E402

NOTE_PAT = re.compile(r"^(?:note)?\d{3}_")


def detect_defects(root, nodes):
    """Return {node_id: [defect_code, ...]}. Only conditions that are
    actually true of the files — nothing inferred, nothing predicted."""
    d = collections.defaultdict(list)
    by_num = collections.defaultdict(list)

    for n in nodes:
        p = n["id"]

        # whitespace in any path component breaks Windows checkouts
        for part in p.split("/"):
            if part != part.strip():
                d[p].append("whitespace")
                break

        if n["kind"] == "dir":
            continue

        full = os.path.join(root, p)
        try:
            if os.path.getsize(full) == 0:
                d[p].append("empty")
        except OSError:
            pass

        if p.startswith(("research_notes/", "notes/")) and p.endswith(".md"):
            base = os.path.basename(p)
            if not NOTE_PAT.match(base):
                d[p].append("unindexed")
            else:
                m = NUM_RE.match(base)
                if m:
                    by_num[m.group(1)].append(p)
                try:
                    txt = open(full, encoding="utf-8", errors="replace").read()
                    if not STATUS_RE.search(txt):
                        d[p].append("nostatus")
                except OSError:
                    pass

    for num, group in by_num.items():
        if len(group) > 1:
            for p in group:
                d[p].append("collision")

    return {k: v for k, v in d.items() if v}


def git_ages(root):
    """{path: unix_seconds_of_last_commit}. One subprocess, not one per file."""
    try:
        out = subprocess.run(
            ["git", "-C", root, "log", "--no-merges",
             "--pretty=format:@%ct", "--name-only"],
            capture_output=True, text=True, timeout=45,
        )
        if out.returncode != 0:
            return {}
    except (OSError, subprocess.SubprocessError):
        return {}

    ages, ts = {}, None
    for line in out.stdout.splitlines():
        if line.startswith("@"):
            try:
                ts = int(line[1:])
            except ValueError:
                ts = None
        elif line and ts:
            ages.setdefault(line.strip(), ts)   # first hit = most recent
    return ages


def build(root):
    p = scan_files(root)
    defects = detect_defects(root, p["nodes"])
    ages = git_ages(root)

    now = int(datetime.datetime.now().timestamp())
    span = 1
    if ages:
        oldest = min(ages.values())
        span = max(1, now - oldest)

    for n in p["nodes"]:
        n["def"] = defects.get(n["id"], [])
        t = ages.get(n["id"])
        # 1.0 = newest commit in history, 0.0 = oldest
        n["age"] = round(1.0 - (now - t) / span, 4) if t else None

    counts = collections.Counter(c for v in defects.values() for c in v)
    p["defects"] = {
        "total_nodes": len(defects),
        "by_code": dict(counts),
        "nodes": {k: v for k, v in defects.items()},
    }
    p["has_age"] = bool(ages)
    p["generated"] = datetime.date.today().isoformat()
    return p


def selftest():
    print("=" * 62)
    print("build_galaxy.py — ANTI-VACUITY SELF-TEST")
    print("=" * 62)
    ok = total = 0

    with tempfile.TemporaryDirectory(dir=os.path.expanduser("~")) as d:
        rn = os.path.join(d, "research_notes")
        os.makedirs(rn)

        # a clean note must produce NO defects
        open(os.path.join(rn, "001_clean.md"), "w").write(
            "# Note #001 — Clean\n**Status:** Draft\n\nBody.\n")
        total += 1
        p = build(d)
        if p["defects"]["total_nodes"] == 0:
            print("[PASS] clean note -> 0 defects  (the detector can report null)")
            ok += 1
        else:
            print(f"[FAIL] clean note flagged: {p['defects']}")

        # each defect class must be found exactly once
        open(os.path.join(rn, "002_nostatus.md"), "w").write("# Note #002\n\nNo label.\n")
        open(os.path.join(rn, "README.md"), "w").write("# not a note\n")
        open(os.path.join(rn, "003_zero.md"), "w").write("")
        os.makedirs(os.path.join(d, "bad ", ), exist_ok=True)
        open(os.path.join(d, "bad ", "x.txt"), "w").write("y")
        total += 1
        p = build(d)
        c = p["defects"]["by_code"]
        # whitespace = 2: the directory "bad " AND the file "bad /x.txt" both
        # carry a broken path component. Both break a Windows checkout, so
        # flagging both is correct — the first version of this test expected 1
        # and the gate caught the wrong expectation. Kept as written.
        want = {"nostatus": 2, "unindexed": 1, "empty": 1, "whitespace": 2}
        # 003_zero.md is both empty AND missing a status label
        got = {k: c.get(k, 0) for k in want}
        if got == want:
            print(f"[PASS] each defect class found exactly once  {got}")
            ok += 1
        else:
            print(f"[FAIL] defect counts {got}, expected {want}")

        # collisions need two files claiming one number
        open(os.path.join(rn, "004_first.md"), "w").write("# A\n**Status:** Draft\n")
        os.makedirs(os.path.join(d, "notes"), exist_ok=True)
        open(os.path.join(d, "notes", "004_second.md"), "w").write("# B\n**Status:** Draft\n")
        total += 1
        p = build(d)
        if p["defects"]["by_code"].get("collision") == 2:
            print("[PASS] one number, two files -> collision on both")
            ok += 1
        else:
            print(f"[FAIL] collision = {p['defects']['by_code'].get('collision')} (want 2)")

        # age must degrade gracefully with no git repo present
        total += 1
        p = build(d)
        if p["has_age"] is False and all(n["age"] is None for n in p["nodes"]):
            print("[PASS] no git repo -> age is None, no fabricated timestamps")
            ok += 1
        else:
            print("[FAIL] age fabricated without git")

    print()
    print(f"RESULT: {ok}/{total} checks passed")
    print("=" * 62)
    return ok == total


SHELL = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Principia Artificialis — Galaxy</title>
<!-- principia-graph-generated -->
<style>
  :root{
    --void:#04060A; --panel:#0A0F17; --rule:#182231; --text:#DAE6F4;
    --dim:#7288A3; --faint:#3B4A5E; --hot:#FFB454; --bad:#FF6B5B;
    --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
    --serif:Georgia,"Iowan Old Style",serif;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{height:100%;background:var(--void);color:var(--text);
    font-family:var(--mono);overflow:hidden;-webkit-text-size-adjust:100%}
  canvas{position:fixed;inset:0;width:100vw;height:100vh;touch-action:none;cursor:grab}
  canvas.g{cursor:grabbing}

  #hud{position:fixed;top:0;left:0;bottom:0;width:262px;z-index:10;
    background:rgba(10,15,23,.94);border-right:1px solid var(--rule);
    padding:18px 16px;overflow-y:auto}
  h1{font-family:var(--serif);font-size:18px;font-weight:400;line-height:1.15}
  h1 em{font-style:italic;color:var(--dim);display:block;font-size:14px}
  .stamp{font-size:9px;letter-spacing:.15em;text-transform:uppercase;
    color:var(--faint);margin:5px 0 16px}

  #q{width:100%;background:#070B12;border:1px solid var(--rule);color:var(--text);
    font-family:var(--mono);font-size:12px;padding:7px 9px;border-radius:3px;
    margin-bottom:16px;outline:none}
  #q:focus{border-color:#2E4053}
  #q::placeholder{color:var(--faint)}

  .card{border-left:2px solid var(--hot);padding:10px 12px;margin-bottom:14px;
    background:rgba(255,180,84,.05);cursor:pointer;user-select:none}
  .card.bad{border-color:var(--bad);background:rgba(255,107,91,.06)}
  .card .n{font-family:var(--serif);font-size:30px;line-height:1;color:var(--hot);
    font-variant-numeric:tabular-nums}
  .card.bad .n{color:var(--bad)}
  .card .l{font-size:9px;letter-spacing:.09em;text-transform:uppercase;
    color:var(--dim);margin-top:3px;line-height:1.5}
  .card.on{outline:1px solid currentColor}

  .sec{font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:var(--faint);
    padding-bottom:5px;margin:0 0 7px;border-bottom:1px solid var(--rule)}
  .g{margin-bottom:16px}
  .r{display:flex;justify-content:space-between;font-size:11.5px;padding:2px 0;
    color:var(--dim)}
  .r b{color:var(--text);font-weight:500;font-variant-numeric:tabular-nums}
  .r.c{cursor:pointer;user-select:none}
  .r.c:hover b{color:var(--hot)}
  .r.off{opacity:.32}

  .k{display:flex;align-items:center;gap:7px;font-size:11px;color:var(--dim);
    padding:2px 0;cursor:pointer;user-select:none}
  .k.off{opacity:.3}
  .sw{width:8px;height:8px;border-radius:50%;flex:none;box-shadow:0 0 6px currentColor}

  .btn{display:inline-block;font-size:10px;letter-spacing:.06em;text-transform:uppercase;
    border:1px solid var(--rule);padding:5px 9px;margin:0 4px 4px 0;color:var(--dim);
    cursor:pointer;user-select:none;border-radius:2px}
  .btn.on{border-color:var(--hot);color:var(--hot)}

  #tip{position:fixed;display:none;max-width:290px;padding:11px 13px;z-index:30;
    background:rgba(10,15,23,.96);border:1px solid #26313F;pointer-events:none}
  #tip .p{font-size:9px;letter-spacing:.12em;color:var(--faint);word-break:break-all}
  #tip .t{font-family:var(--serif);font-size:14px;line-height:1.3;margin:3px 0 6px;
    word-break:break-word}
  #tip .m{font-size:10.5px;color:var(--dim);line-height:1.5}
  #tip .d{color:var(--bad);margin-top:5px;font-size:10px}

  #bar{position:fixed;left:262px;right:0;bottom:0;padding:7px 14px;font-size:10px;
    color:var(--faint);z-index:5;background:linear-gradient(transparent,var(--void) 60%)}
  @media(max-width:760px){
    #hud{width:100%;bottom:auto;max-height:46vh;border-right:0;
      border-bottom:1px solid var(--rule)}
    #bar{left:0}
  }
</style>
</head>
<body>
<canvas id="c"></canvas>

<aside id="hud">
  <h1>Galaxy<em>Principia Artificialis</em></h1>
  <div class="stamp" id="stamp"></div>

  <input id="q" placeholder="filter by name or path…" autocomplete="off" spellcheck="false">

  <div class="card" id="cE"><div class="n" id="nE">—</div>
    <div class="l">measured edges<br>none invented</div></div>

  <div class="card bad" id="cD"><div class="n" id="nD">—</div>
    <div class="l">files with a defect<br>tap to isolate</div></div>

  <div class="g">
    <div class="sec">Nodes</div>
    <div class="r"><span>files</span><b id="sF">—</b></div>
    <div class="r"><span>directories</span><b id="sD">—</b></div>
    <div class="r"><span>orphans</span><b id="sO">—</b></div>
  </div>

  <div class="g">
    <div class="sec">Edges — tap to mute</div>
    <div class="r c" data-e="contains"><span>contains</span><b id="eC">—</b></div>
    <div class="r c" data-e="sibling"><span>sibling</span><b id="eS">—</b></div>
    <div class="r c" data-e="builds_on"><span>builds on</span><b id="eB">—</b></div>
  </div>

  <div class="g">
    <div class="sec">Defects found</div>
    <div id="dl"></div>
  </div>

  <div class="g">
    <div class="sec">Colour</div>
    <span class="btn on" id="mK">by kind</span><span class="btn" id="mA">by age</span>
  </div>

  <div class="g">
    <div class="sec">Kind — tap to mute</div>
    <div id="leg"></div>
  </div>

  <div class="g">
    <div class="sec">Keys</div>
    <div class="r" style="display:block;line-height:1.6">
      <span><b>D</b> defects &middot; <b>A</b> age &middot; <b>R</b> reset
      &middot; <b>B</b> bloom<br>tap a node to isolate its neighbours</span>
    </div>
  </div>
</aside>

<div id="tip"><div class="p" id="tp"></div><div class="t" id="tt"></div>
  <div class="m" id="tm"></div><div class="d" id="td"></div></div>

<div id="bar">drag to orbit &middot; pinch or scroll to zoom &middot; tap empty space to clear</div>

<script id="D" type="application/json">__DATA__</script>
<script>
(function(){
"use strict";
var D=JSON.parse(document.getElementById('D').textContent),S=D.stats,DF=D.defects;
function T(i,v){var e=document.getElementById(i);if(e)e.textContent=v;}
T('stamp','generated '+D.generated+(D.has_age?'':'  ·  no git history'));
T('nE',S.edges);T('nD',DF.total_nodes);T('sF',S.files);T('sD',S.dirs);T('sO',S.orphans);
T('eC',S.contains);T('eS',S.sibling);T('eB',S.builds_on);

var DESC={whitespace:'whitespace in path',unindexed:'invisible to index',
  nostatus:'no Status label',collision:'number claimed twice',empty:'zero bytes'};
var dl=document.getElementById('dl');
Object.keys(DF.by_code).sort().forEach(function(k){
  var d=document.createElement('div');d.className='r';
  d.innerHTML='<span>'+(DESC[k]||k)+'</span><b>'+DF.by_code[k]+'</b>';dl.appendChild(d);});
if(!Object.keys(DF.by_code).length)dl.innerHTML='<div class="r"><span>none</span><b>0</b></div>';

var COL={dir:'#5B7FA8',doc:'#93AECB',code:'#4FD6B8',figure:'#C77DD6',
  data:'#E0C060',proof:'#FF7B6B',build:'#66788E',other:'#42526A',
  refuted:'#FFB454',verified:'#4FD6B8',draft:'#93AECB',
  speculative:'#66799A',unlabeled:'#42526A'};
var KINDS=[['dir','directory'],['doc','markdown'],['code','python'],
  ['figure','figure'],['data','data'],['refuted','refuted, kept']];
var muteK={},muteE={};
var leg=document.getElementById('leg');
KINDS.forEach(function(p){var e=document.createElement('div');e.className='k';
  e.dataset.k=p[0];
  e.innerHTML='<span class="sw" style="background:'+COL[p[0]]+';color:'+COL[p[0]]+'"></span>'+p[1];
  e.onclick=function(){muteK[p[0]]=!muteK[p[0]];e.classList.toggle('off');paint();};
  leg.appendChild(e);});
document.querySelectorAll('.r.c').forEach(function(r){
  r.onclick=function(){var k=r.dataset.e;muteE[k]=!muteE[k];r.classList.toggle('off');paint();};});

function ageCol(a){ // cold indigo -> hot amber
  if(a===null||a===undefined)return '#2C3746';
  var t=Math.max(0,Math.min(1,a));
  var r=Math.round(56+(255-56)*t),g=Math.round(72+(180-72)*t),b=Math.round(120+(84-120)*t);
  return 'rgb('+r+','+g+','+b+')';
}
var mode='kind';
document.getElementById('mK').onclick=function(){setMode('kind');};
document.getElementById('mA').onclick=function(){setMode('age');};
function setMode(m){mode=m;
  document.getElementById('mK').classList.toggle('on',m==='kind');
  document.getElementById('mA').classList.toggle('on',m==='age');paint();}

var N=D.nodes.map(function(n){return Object.assign({},n);});
var ix={};N.forEach(function(n,i){ix[n.id]=i;});
var E=D.edges.filter(function(e){return ix[e.source]!==undefined&&ix[e.target]!==undefined;})
             .map(function(e){return{s:ix[e.source],t:ix[e.target],k:e.kind};});
var adj={};E.forEach(function(e){(adj[e.s]=adj[e.s]||[]).push(e.t);
                                (adj[e.t]=adj[e.t]||[]).push(e.s);});

var sd=7919;function rnd(){sd=(sd*1103515245+12345)&0x7fffffff;return sd/0x7fffffff;}
N.forEach(function(n){
  var u=rnd()*2-1,th=rnd()*6.2832,r=165*Math.cbrt(rnd())+42,s=Math.sqrt(1-u*u);
  n.x=r*s*Math.cos(th);n.y=r*s*Math.sin(th);n.z=r*u;n.vx=n.vy=n.vz=0;
  n.m=n.kind==='dir'?3.4:1;
  n.rad=n.kind==='dir'?3.6:(1.5+Math.min(3.4,Math.log(1+n.bytes/850)));
  n.bad=(n.def&&n.def.length)>0;
});

var cv=document.getElementById('c'),cx=cv.getContext('2d');
var bl=document.createElement('canvas'),bx=bl.getContext('2d');
var DPR=1,BS=0.5,bloom=true;
function fit(){DPR=Math.min(devicePixelRatio||1,2);
  cv.width=Math.round(innerWidth*DPR);cv.height=Math.round(innerHeight*DPR);
  bl.width=Math.max(1,Math.round(cv.width*BS));bl.height=Math.max(1,Math.round(cv.height*BS));}
addEventListener('resize',function(){fit();paint();});fit();

var rY=0.45,rX=-0.2,zm=innerWidth<760?1.0:1.65,al=1,auto=true;
var focus=null,near={},filt='';

function tick(){
  if(al<0.0025)return false;al*=0.9865;
  var i,j,a,b,dx,dy,dz,d2,d,f,u;
  for(i=0;i<N.length;i++){a=N[i];
    for(j=i+1;j<N.length;j++){b=N[j];
      dx=b.x-a.x;dy=b.y-a.y;dz=b.z-a.z;d2=dx*dx+dy*dy+dz*dz;
      if(d2<1e-4){dx=rnd()-.5;dy=rnd()-.5;dz=rnd()-.5;d2=1e-4;}
      if(d2>240000)continue;
      d=Math.sqrt(d2);f=880*a.m*b.m/d2/d;
      a.vx-=dx*f;a.vy-=dy*f;a.vz-=dz*f;b.vx+=dx*f;b.vy+=dy*f;b.vz+=dz*f;}}
  for(i=0;i<E.length;i++){a=N[E[i].s];b=N[E[i].t];
    dx=b.x-a.x;dy=b.y-a.y;dz=b.z-a.z;
    d=Math.sqrt(dx*dx+dy*dy+dz*dz)||1e-4;
    u=E[i].k==='contains'?45:(E[i].k==='sibling'?25:60);
    f=(d-u)*(E[i].k==='sibling'?0.031:0.016)/d;
    a.vx+=dx*f;a.vy+=dy*f;a.vz+=dz*f;b.vx-=dx*f;b.vy-=dy*f;b.vz-=dz*f;}
  for(i=0;i<N.length;i++){a=N[i];
    a.vx-=a.x*0.0072;a.vy-=a.y*0.0072;a.vz-=a.z*0.0072;
    a.x+=a.vx*al*1.7;a.y+=a.vy*al*1.7;a.z+=a.vz*al*1.7;
    a.vx*=0.80;a.vy*=0.80;a.vz*=0.80;}
  return true;
}

var W,H,CX,CY;
function proj(n){
  var cy=Math.cos(rY),sy=Math.sin(rY),cq=Math.cos(rX),sq=Math.sin(rX);
  var x=n.x*cy-n.z*sy,z=n.x*sy+n.z*cy,y=n.y*cq-z*sq;z=n.y*sq+z*cq;
  var p=740/(740+z+410);
  n.px=CX+x*p*zm;n.py=CY+y*p*zm;n.pz=z;n.pp=p;
}
function vis(n){
  if(muteK[n.kind]||(n.cls==='refuted'&&muteK.refuted))return false;
  if(filt&&n.id.toLowerCase().indexOf(filt)<0)return false;
  return true;
}
function lum(n){ // how bright this node should be given focus/filter state
  if(focus!==null){ if(n===N[focus])return 1; return near[N.indexOf(n)]?0.8:0.10; }
  if(filt)return n.id.toLowerCase().indexOf(filt)>=0?1:0.07;
  return 1;
}
function ncol(n){return mode==='age'?ageCol(n.age):(COL[n.cls]||COL[n.kind]||COL.other);}

function paint(){
  W=innerWidth;H=innerHeight;CX=W/2+(W>760?124:0);CY=H/2;
  var i,n;
  for(i=0;i<N.length;i++)proj(N[i]);
  var ord=N.slice().sort(function(p,q){return q.pz-p.pz;});

  // ---- pass 1: glow buffer at half res ----
  if(bloom){
    bx.setTransform(1,0,0,1,0,0);bx.clearRect(0,0,bl.width,bl.height);
    var k=DPR*BS;
    bx.globalCompositeOperation='lighter';
    for(i=0;i<ord.length;i++){n=ord[i];
      if(!vis(n))continue;
      var L=lum(n);if(L<0.2)continue;
      var r=Math.max(.6,n.rad*n.pp*zm)*k,dep=Math.max(.12,Math.min(1,n.pp));
      var g=bx.createRadialGradient(n.px*k,n.py*k,0,n.px*k,n.py*k,r*9);
      var c=n.bad&&showBad?'#FF6B5B':ncol(n);
      g.addColorStop(0,rgba(c,.55*dep*L));g.addColorStop(.4,rgba(c,.10*dep*L));
      g.addColorStop(1,rgba(c,0));
      bx.fillStyle=g;bx.beginPath();bx.arc(n.px*k,n.py*k,r*9,0,6.2832);bx.fill();}
  }

  // ---- pass 2: scene ----
  cx.setTransform(DPR,0,0,DPR,0,0);
  cx.globalCompositeOperation='source-over';
  var bg=cx.createRadialGradient(CX,CY,0,CX,CY,Math.max(W,H)*.8);
  bg.addColorStop(0,'#0A1220');bg.addColorStop(1,'#04060A');
  cx.fillStyle=bg;cx.fillRect(0,0,W,H);

  if(bloom){ // composite the blurred glow back, twice, for a soft falloff
    cx.globalCompositeOperation='lighter';
    cx.imageSmoothingEnabled=true;
    cx.setTransform(1,0,0,1,0,0);
    cx.globalAlpha=.85;cx.drawImage(bl,0,0,cv.width,cv.height);
    cx.globalAlpha=.45;cx.drawImage(bl,-4,-4,cv.width+8,cv.height+8);
    cx.globalAlpha=1;cx.setTransform(DPR,0,0,DPR,0,0);
  }

  cx.globalCompositeOperation='lighter';
  for(i=0;i<E.length;i++){
    if(muteE[E[i].k])continue;
    var a=N[E[i].s],b=N[E[i].t];
    if(!vis(a)||!vis(b))continue;
    var L=Math.min(lum(a),lum(b));if(L<0.1)continue;
    var dep=Math.max(.08,Math.min(1,(a.pp+b.pp)/2)),c,o;
    if(E[i].k==='sibling'){c='199,125,214';o=.42;}
    else if(E[i].k==='builds_on'){c='79,214,184';o=.36;}
    else{c='66,88,120';o=.15;}
    cx.strokeStyle='rgba('+c+','+(o*dep*L).toFixed(3)+')';
    cx.lineWidth=(E[i].k==='contains'?.6:1.1)*dep;
    cx.beginPath();cx.moveTo(a.px,a.py);cx.lineTo(b.px,b.py);cx.stroke();
  }

  cx.globalCompositeOperation='source-over';
  for(i=0;i<ord.length;i++){n=ord[i];
    if(!vis(n))continue;
    var L=lum(n);
    var r=Math.max(.6,n.rad*n.pp*zm),dep=Math.max(.16,Math.min(1,n.pp));
    cx.fillStyle=rgba(n.bad&&showBad?'#FF6B5B':ncol(n),(.5+.5*dep)*L);
    cx.beginPath();cx.arc(n.px,n.py,r,0,6.2832);cx.fill();
    if(n.bad&&showBad&&L>.3){
      cx.strokeStyle='rgba(255,107,91,'+(0.85*L).toFixed(2)+')';cx.lineWidth=1.3;
      cx.beginPath();cx.arc(n.px,n.py,r+3.6,0,6.2832);cx.stroke();}
    else if(n.cls==='refuted'&&L>.3){
      cx.strokeStyle='rgba(255,180,84,'+(0.7*L).toFixed(2)+')';cx.lineWidth=1.2;
      cx.beginPath();cx.arc(n.px,n.py,r+3.4,0,6.2832);cx.stroke();}
    if(n===hov||(focus!==null&&n===N[focus])){
      cx.strokeStyle='rgba(218,230,244,.95)';cx.lineWidth=1.15;
      cx.beginPath();cx.arc(n.px,n.py,r+6.5,0,6.2832);cx.stroke();}
  }

  cx.font='500 10px '+getComputedStyle(document.body).fontFamily;
  cx.textAlign='center';
  for(i=0;i<N.length;i++){n=N[i];
    if(!vis(n))continue;
    var L=lum(n);
    var lab=(n.kind==='dir'&&n.pp>.6&&zm>.7)||(focus!==null&&(n===N[focus]||near[i]))
            ||(filt&&L>.5&&n.pp>.45);
    if(lab){cx.fillStyle='rgba(154,175,199,'+Math.min(.9,n.pp*L).toFixed(2)+')';
      cx.fillText(n.label,n.px,n.py-n.rad*n.pp*zm-7);}}
}
function rgba(h,a){
  if(h[0]!=='#')return h.replace('rgb(','rgba(').replace(')',','+a.toFixed(3)+')');
  var v=parseInt(h.slice(1),16);
  return 'rgba('+(v>>16)+','+((v>>8)&255)+','+(v&255)+','+a.toFixed(3)+')';}

var showBad=false;
document.getElementById('cD').onclick=function(){
  showBad=!showBad;this.classList.toggle('on',showBad);
  filt='';document.getElementById('q').value='';
  if(showBad){focus=null;near={};}
  paint();};
document.getElementById('cE').onclick=function(){
  focus=null;near={};filt='';showBad=false;
  document.getElementById('q').value='';
  document.getElementById('cD').classList.remove('on');paint();};

document.getElementById('q').oninput=function(){
  filt=this.value.trim().toLowerCase();focus=null;near={};paint();};

var hov=null,tip=document.getElementById('tip');
function pick(mx,my){var best=null,bd=1e9;
  for(var i=0;i<N.length;i++){var n=N[i];if(!vis(n))continue;
    var dx=n.px-mx,dy=n.py-my,d=dx*dx+dy*dy;
    var rr=Math.max(8,n.rad*n.pp*zm+8);rr*=rr;
    if(d<rr&&d<bd){bd=d;best=n;}}
  return best;}
function tipOn(n,mx,my){
  if(!n){tip.style.display='none';hov=null;paint();return;}
  hov=n;
  document.getElementById('tp').textContent=n.id;
  document.getElementById('tt').textContent=n.label;
  var kb=n.bytes>=1024?(n.bytes/1024).toFixed(1)+' KB':n.bytes+' B';
  var age=n.age===null||n.age===undefined?'':'  ·  age '+Math.round(n.age*100)+'%';
  document.getElementById('tm').textContent=
    (n.status?n.status+'\u2003':'')+n.kind+(n.kind==='dir'?'':'  ·  '+kb)+
    '  ·  '+n.deg+' edge'+(n.deg===1?'':'s')+age;
  document.getElementById('td').textContent=
    (n.def&&n.def.length)?'DEFECT: '+n.def.map(function(c){return DESC[c]||c;}).join(', '):'';
  tip.style.display='block';
  var tw=tip.offsetWidth,th=tip.offsetHeight;
  tip.style.left=Math.max(6,Math.min(mx+14,innerWidth-tw-6))+'px';
  tip.style.top=Math.max(6,Math.min(my+14,innerHeight-th-6))+'px';
  paint();}

function setFocus(n){
  if(!n){focus=null;near={};paint();return;}
  var i=N.indexOf(n);focus=i;near={};
  (adj[i]||[]).forEach(function(j){near[j]=1;});
  paint();}

var dn=false,lx=0,ly=0,mv=0;
function pd(x,y){dn=true;lx=x;ly=y;mv=0;auto=false;cv.classList.add('g');}
function pm(x,y){if(dn){rY+=(x-lx)*.0058;rX+=(y-ly)*.0058;
    rX=Math.max(-1.5,Math.min(1.5,rX));mv+=Math.abs(x-lx)+Math.abs(y-ly);
    lx=x;ly=y;paint();}else tipOn(pick(x,y),x,y);}
function pu(x,y){if(dn&&mv<6){var n=pick(x,y);tipOn(n,x,y);setFocus(n);}
  dn=false;cv.classList.remove('g');}
cv.addEventListener('mousedown',function(e){pd(e.clientX,e.clientY);});
addEventListener('mousemove',function(e){pm(e.clientX,e.clientY);});
addEventListener('mouseup',function(e){pu(e.clientX,e.clientY);});
cv.addEventListener('touchstart',function(e){if(e.touches.length===1){
  var t=e.touches[0];pd(t.clientX,t.clientY);}},{passive:true});
cv.addEventListener('touchmove',function(e){if(e.touches.length===1){
  var t=e.touches[0];pm(t.clientX,t.clientY);}},{passive:true});
cv.addEventListener('touchend',function(e){var t=e.changedTouches[0];
  pu(t.clientX,t.clientY);},{passive:true});
cv.addEventListener('wheel',function(e){e.preventDefault();auto=false;
  zm=Math.max(.22,Math.min(8,zm*(e.deltaY<0?1.1:.909)));paint();},{passive:false});
var pdist=0;
cv.addEventListener('touchstart',function(e){if(e.touches.length===2){auto=false;
  pdist=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,
                   e.touches[0].clientY-e.touches[1].clientY);}},{passive:true});
cv.addEventListener('touchmove',function(e){if(e.touches.length===2&&pdist){
  var d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,
                   e.touches[0].clientY-e.touches[1].clientY);
  zm=Math.max(.22,Math.min(8,zm*(d/pdist)));pdist=d;dn=false;paint();}},{passive:true});

addEventListener('keydown',function(e){
  if(e.target.tagName==='INPUT')return;
  var k=e.key.toLowerCase();
  if(k==='d')document.getElementById('cD').click();
  else if(k==='a')setMode(mode==='age'?'kind':'age');
  else if(k==='b'){bloom=!bloom;paint();}
  else if(k==='r')document.getElementById('cE').click();
});

var slow=matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
if(slow){for(var z=0;z<340;z++)tick();al=0;paint();}
else{(function loop(){var live=tick();if(auto)rY+=.0007;
  if(live||auto){paint();requestAnimationFrame(loop);}else paint();})();}
})();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="galaxy.html")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(0 if selftest() else 1)

    root = os.path.abspath(a.root)
    p = build(root)
    data = json.dumps(p, separators=(",", ":")).replace("</", "<\\/")
    out = os.path.join(root, a.out)
    with open(out, "w", encoding="utf-8") as f:
        f.write(SHELL.replace("__DATA__", data))

    s, d = p["stats"], p["defects"]
    print("GALAXY — measured")
    print(f"  files            {s['files']}")
    print(f"  directories      {s['dirs']}")
    print(f"  nodes            {s['nodes']}")
    print(f"  edges            {s['edges']}"
          f"   (contains {s['contains']}, sibling {s['sibling']},"
          f" builds_on {s['builds_on']})")
    print(f"  orphans          {s['orphans']}")
    print()
    print(f"  DEFECTS on {d['total_nodes']} nodes")
    for k in sorted(d["by_code"]):
        print(f"    {k:12} {d['by_code'][k]}")
    print()
    print(f"  git history      {'read' if p['has_age'] else 'UNAVAILABLE — age disabled'}")
    print()
    print(f"wrote {out}  ({os.path.getsize(out)} bytes, 0 external requests)")


if __name__ == "__main__":
    main()
