#!/usr/bin/env python3
"""
build_filegraph.py — render EVERY file in the repo as a node.

Companion to build_graph.py (which renders only the note series).
Imports its scanner so there is one definition of what an edge is.

Edge kinds, all measured, none invented:
    contains   directory holds file            243
    sibling    same note number, different file  95   (note <-> figure <-> script)
    builds_on  note header citation              41

Renders with additive-glow compositing on canvas 2D: no WebGL, no CDN, no
backdrop-filter. Works offline, survives Adreno, runs on the S25.

    python scripts/build_filegraph.py             # writes graph_files.html
    python scripts/build_filegraph.py --selftest  # anti-vacuity gate
"""

import argparse
import datetime
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_graph import scan_files  # noqa: E402  — single source of edge truth


def selftest():
    """The instrument must be able to report an empty graph."""
    print("=" * 62)
    print("build_filegraph.py — ANTI-VACUITY SELF-TEST")
    print("=" * 62)
    ok = total = 0

    with tempfile.TemporaryDirectory(dir=os.path.expanduser("~")) as d:
        # Case 1: empty repo -> 0 files, 0 edges
        total += 1
        p = scan_files(d)
        if p["stats"]["files"] == 0 and p["stats"]["edges"] == 0:
            print("[PASS] empty repo: 0 files, 0 edges")
            ok += 1
        else:
            print(f"[FAIL] empty repo: {p['stats']}")

        # Case 2: two unrelated files -> containment only, no siblings
        os.makedirs(os.path.join(d, "a"))
        open(os.path.join(d, "a", "alpha.txt"), "w").write("x")
        open(os.path.join(d, "a", "beta.txt"), "w").write("y")
        total += 1
        p = scan_files(d)
        if p["stats"]["sibling"] == 0 and p["stats"]["builds_on"] == 0:
            print(f"[PASS] unrelated files: 0 sibling, 0 builds_on "
                  f"({p['stats']['contains']} contains)")
            ok += 1
        else:
            print(f"[FAIL] unrelated files invented edges: {p['stats']}")

        # Case 3: matched note number across dirs -> exactly 1 sibling edge
        os.makedirs(os.path.join(d, "research_notes"))
        os.makedirs(os.path.join(d, "figures"))
        open(os.path.join(d, "research_notes", "077_thing.md"), "w").write(
            "# Note #077\n**Status:** Draft\n")
        open(os.path.join(d, "figures", "note077_pic.png"), "w").write("x")
        total += 1
        p = scan_files(d)
        if p["stats"]["sibling"] == 1:
            print("[PASS] note077 md + note077 png -> exactly 1 sibling edge")
            ok += 1
        else:
            print(f"[FAIL] sibling count = {p['stats']['sibling']} (expected 1)")

        # Case 4: a number that matches nothing must NOT create an edge
        open(os.path.join(d, "research_notes", "088_lonely.md"), "w").write(
            "# Note #088\n**Status:** Draft\n**Builds on:** #999 (does not exist)\n")
        total += 1
        p = scan_files(d)
        if p["stats"]["sibling"] == 1 and p["stats"]["builds_on"] == 0:
            print("[PASS] #999 does not resolve -> no phantom edge")
            ok += 1
        else:
            print(f"[FAIL] phantom edge created: {p['stats']}")

    print()
    print(f"RESULT: {ok}/{total} checks passed")
    print("=" * 62)
    return ok == total


SHELL = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Principia Artificialis — File Graph</title>
<style>
  :root{
    --void:#05070C; --panel:#0C1119; --rule:#1A2431; --text:#D6E2F0;
    --dim:#7288A3; --faint:#3D4C60; --hot:#FFB454;
    --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
    --serif:Georgia,"Iowan Old Style",serif;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{height:100%;background:var(--void);color:var(--text);
    font-family:var(--mono);overflow:hidden;-webkit-text-size-adjust:100%}
  canvas{display:block;width:100vw;height:100vh;touch-action:none;cursor:grab}
  canvas.drag{cursor:grabbing}

  .panel{position:fixed;background:rgba(12,17,25,.93);border:1px solid var(--rule)}

  #hud{top:0;left:0;bottom:0;width:270px;border-width:0 1px 0 0;
    padding:20px 18px;overflow-y:auto;z-index:10}
  #hud h1{font-family:var(--serif);font-size:19px;font-weight:400;line-height:1.15}
  #hud h1 em{font-style:italic;color:var(--dim);display:block;font-size:15px}
  .stamp{font-size:9px;letter-spacing:.16em;text-transform:uppercase;
    color:var(--faint);margin:6px 0 20px}

  .hero{border-left:2px solid var(--hot);padding:11px 13px;
    background:rgba(255,180,84,.05);margin-bottom:20px}
  .hero .n{font-family:var(--serif);font-size:34px;line-height:1;color:var(--hot);
    font-variant-numeric:tabular-nums}
  .hero .l{font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;
    color:var(--dim);margin-top:4px;line-height:1.5}

  .sec{font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:var(--faint);
    padding-bottom:6px;margin:0 0 8px;border-bottom:1px solid var(--rule)}
  .grp{margin-bottom:20px}
  .r{display:flex;justify-content:space-between;font-size:11.5px;
    padding:2.5px 0;color:var(--dim)}
  .r b{color:var(--text);font-weight:500;font-variant-numeric:tabular-nums}
  .k{display:flex;align-items:center;gap:8px;font-size:11px;color:var(--dim);padding:2.5px 0}
  .d{width:8px;height:8px;border-radius:50%;flex:none;box-shadow:0 0 7px currentColor}

  #tip{display:none;max-width:290px;padding:12px 14px;z-index:30;pointer-events:none}
  #tip .p{font-size:9px;letter-spacing:.13em;color:var(--faint);
    text-transform:uppercase;word-break:break-all}
  #tip .t{font-family:var(--serif);font-size:14.5px;line-height:1.3;margin:4px 0 7px;
    word-break:break-word}
  #tip .m{font-size:11px;color:var(--dim);line-height:1.55}

  #bar{position:fixed;left:270px;right:0;bottom:0;padding:8px 16px;font-size:10px;
    color:var(--faint);letter-spacing:.04em;z-index:5;
    background:linear-gradient(transparent,var(--void) 65%)}
  @media(max-width:760px){
    #hud{width:100%;bottom:auto;max-height:44vh;border-width:0 0 1px 0}
    #bar{left:0}
  }
</style>
</head>
<body>
<canvas id="c"></canvas>

<aside class="panel" id="hud">
  <h1>File Graph<em>Principia Artificialis</em></h1>
  <div class="stamp" id="stamp"></div>

  <div class="hero">
    <div class="n" id="hE">—</div>
    <div class="l">measured edges<br>none invented</div>
  </div>

  <div class="grp">
    <div class="sec">Nodes</div>
    <div class="r"><span>files</span><b id="sF">—</b></div>
    <div class="r"><span>directories</span><b id="sD">—</b></div>
    <div class="r"><span>orphans</span><b id="sO">—</b></div>
  </div>

  <div class="grp">
    <div class="sec">Edges by kind</div>
    <div class="r"><span>contains</span><b id="eC">—</b></div>
    <div class="r"><span>sibling</span><b id="eS">—</b></div>
    <div class="r"><span>builds&nbsp;on</span><b id="eB">—</b></div>
  </div>

  <div class="grp">
    <div class="sec">Legend</div>
    <div id="leg"></div>
  </div>

  <div class="grp">
    <div class="sec">Reading it</div>
    <div class="r" style="display:block;line-height:1.55">
      <span>Amber halo marks a note whose registered claim failed and was
      kept. Sibling edges join a note to its figure and its reference
      script &mdash; the same artifact in three files.</span>
    </div>
  </div>
</aside>

<div class="panel" id="tip">
  <div class="p" id="tp"></div>
  <div class="t" id="tt"></div>
  <div class="m" id="tm"></div>
</div>

<div id="bar">drag to orbit &middot; pinch or scroll to zoom &middot; tap a node</div>

<script id="D" type="application/json">__DATA__</script>
<script>
(function(){
"use strict";
var D=JSON.parse(document.getElementById('D').textContent),S=D.stats;
function T(i,v){var e=document.getElementById(i);if(e)e.textContent=v;}
T('stamp',D.generated||'');T('hE',S.edges);T('sF',S.files);T('sD',S.dirs);
T('sO',S.orphans);T('eC',S.contains);T('eS',S.sibling);T('eB',S.builds_on);

var COL={dir:'#5B7FA8',doc:'#8FA8C4',code:'#4FD6B8',figure:'#C77DD6',
         data:'#E0C060',proof:'#FF7B6B',build:'#6B7C93',other:'#46566B',
         refuted:'#FFB454',verified:'#4FD6B8',draft:'#8FA8C4',
         speculative:'#6A7E9B',unlabeled:'#46566B'};
var LEG=[['dir','directory'],['doc','markdown note'],['code','python / shell'],
         ['figure','figure or gif'],['data','data + logs'],['refuted','refuted, kept']];
var lg=document.getElementById('leg');
LEG.forEach(function(p){var d=document.createElement('div');d.className='k';
  d.innerHTML='<span class="d" style="background:'+COL[p[0]]+';color:'+COL[p[0]]+'"></span>'+p[1];
  lg.appendChild(d);});

var N=D.nodes.map(function(n){return Object.assign({},n);});
var ix={};N.forEach(function(n,i){ix[n.id]=i;});
var E=D.edges.filter(function(e){return ix[e.source]!==undefined&&ix[e.target]!==undefined;})
             .map(function(e){return {s:ix[e.source],t:ix[e.target],k:e.kind};});

// deterministic seed so the layout is reproducible run to run
var _s=1337;function rnd(){_s=(_s*1103515245+12345)&0x7fffffff;return _s/0x7fffffff;}
N.forEach(function(n,i){
  var u=rnd()*2-1,th=rnd()*6.2832,r=170*Math.cbrt(rnd())+40;
  var s=Math.sqrt(1-u*u);
  n.x=r*s*Math.cos(th);n.y=r*s*Math.sin(th);n.z=r*u;
  n.vx=n.vy=n.vz=0;
  n.m=n.kind==='dir'?3.2:1;
  n.rad=n.kind==='dir'?3.4:(1.5+Math.min(3.2,Math.log(1+n.bytes/900)));
  n.col=COL[n.cls]||COL[n.kind]||COL.other;
});

var cv=document.getElementById('c'),cx=cv.getContext('2d'),DPR=1;
function fit(){DPR=Math.min(devicePixelRatio||1,2);
  cv.width=Math.round(cv.clientWidth*DPR);cv.height=Math.round(cv.clientHeight*DPR);}
addEventListener('resize',function(){fit();paint();});fit();

var rotY=0.4,rotX=-0.22,zoom=innerWidth<760?1.05:1.7,alpha=1,auto=true;

function tick(){
  if(alpha<0.0025)return false;
  alpha*=0.986;
  var i,j,a,b,dx,dy,dz,d2,d,f,u;
  for(i=0;i<N.length;i++){
    a=N[i];
    for(j=i+1;j<N.length;j++){
      b=N[j];dx=b.x-a.x;dy=b.y-a.y;dz=b.z-a.z;d2=dx*dx+dy*dy+dz*dz;
      if(d2<1e-4){dx=rnd()-.5;dy=rnd()-.5;dz=rnd()-.5;d2=1e-4;}
      if(d2>250000)continue;
      d=Math.sqrt(d2);f=900*a.m*b.m/d2/d;
      a.vx-=dx*f;a.vy-=dy*f;a.vz-=dz*f;
      b.vx+=dx*f;b.vy+=dy*f;b.vz+=dz*f;
    }
  }
  for(i=0;i<E.length;i++){
    a=N[E[i].s];b=N[E[i].t];
    dx=b.x-a.x;dy=b.y-a.y;dz=b.z-a.z;
    d=Math.sqrt(dx*dx+dy*dy+dz*dz)||1e-4;
    u=E[i].k==='contains'?46:(E[i].k==='sibling'?26:62);
    f=(d-u)*(E[i].k==='sibling'?0.030:0.016)/d;
    a.vx+=dx*f;a.vy+=dy*f;a.vz+=dz*f;
    b.vx-=dx*f;b.vy-=dy*f;b.vz-=dz*f;
  }
  for(i=0;i<N.length;i++){
    a=N[i];
    a.vx-=a.x*0.0075;a.vy-=a.y*0.0075;a.vz-=a.z*0.0075;
    a.x+=a.vx*alpha*1.7;a.y+=a.vy*alpha*1.7;a.z+=a.vz*alpha*1.7;
    a.vx*=0.80;a.vy*=0.80;a.vz*=0.80;
  }
  return true;
}

var W,H,CXp,CYp;
function proj(n){
  var cy=Math.cos(rotY),sy=Math.sin(rotY),cxr=Math.cos(rotX),sxr=Math.sin(rotX);
  var x=n.x*cy-n.z*sy, z=n.x*sy+n.z*cy;
  var y=n.y*cxr-z*sxr;  z=n.y*sxr+z*cxr;
  var p=760/(760+z+420);
  n.px=CXp+x*p*zoom; n.py=CYp+y*p*zoom; n.pz=z; n.pp=p;
}

function paint(){
  W=cv.clientWidth;H=cv.clientHeight;CXp=W/2+(W>760?135:0);CYp=H/2;
  cx.setTransform(DPR,0,0,DPR,0,0);
  cx.globalCompositeOperation='source-over';
  var g=cx.createRadialGradient(CXp,CYp,0,CXp,CYp,Math.max(W,H)*.78);
  g.addColorStop(0,'#0B1220');g.addColorStop(1,'#05070C');
  cx.fillStyle=g;cx.fillRect(0,0,W,H);

  var i,n;
  for(i=0;i<N.length;i++)proj(N[i]);

  // edges, additive, depth-faded
  cx.globalCompositeOperation='lighter';
  for(i=0;i<E.length;i++){
    var a=N[E[i].s],b=N[E[i].t];
    var dep=Math.max(.08,Math.min(1,(a.pp+b.pp)/2));
    var o,c;
    if(E[i].k==='sibling'){c='199,125,214';o=.40*dep;}
    else if(E[i].k==='builds_on'){c='79,214,184';o=.34*dep;}
    else {c='70,92,124';o=.16*dep;}
    cx.strokeStyle='rgba('+c+','+o.toFixed(3)+')';
    cx.lineWidth=(E[i].k==='contains'?.6:1.05)*dep;
    cx.beginPath();cx.moveTo(a.px,a.py);cx.lineTo(b.px,b.py);cx.stroke();
  }

  // nodes back-to-front so nearer glow sits on top
  var ord=N.slice().sort(function(p,q){return q.pz-p.pz;});
  for(i=0;i<ord.length;i++){
    n=ord[i];
    var r=Math.max(.7,n.rad*n.pp*zoom),dep=Math.max(.1,Math.min(1,n.pp));
    var gr=cx.createRadialGradient(n.px,n.py,0,n.px,n.py,r*7);
    gr.addColorStop(0,hex(n.col,.62*dep));
    gr.addColorStop(.35,hex(n.col,.14*dep));
    gr.addColorStop(1,hex(n.col,0));
    cx.fillStyle=gr;
    cx.beginPath();cx.arc(n.px,n.py,r*7,0,6.2832);cx.fill();
  }
  cx.globalCompositeOperation='source-over';
  for(i=0;i<ord.length;i++){
    n=ord[i];
    var r=Math.max(.7,n.rad*n.pp*zoom),dep=Math.max(.15,Math.min(1,n.pp));
    cx.fillStyle=hex(n.col,.55+.45*dep);
    cx.beginPath();cx.arc(n.px,n.py,r,0,6.2832);cx.fill();
    if(n.cls==='refuted'){
      cx.strokeStyle='rgba(255,180,84,.72)';cx.lineWidth=1.25;
      cx.beginPath();cx.arc(n.px,n.py,r+3.4,0,6.2832);cx.stroke();
    }
    if(n===hov){
      cx.strokeStyle='rgba(214,226,240,.92)';cx.lineWidth=1.15;
      cx.beginPath();cx.arc(n.px,n.py,r+6,0,6.2832);cx.stroke();
    }
  }

  // directory labels only — the structure, not every filename
  cx.font='500 10px '+getComputedStyle(document.body).fontFamily;
  cx.textAlign='center';
  for(i=0;i<N.length;i++){
    n=N[i];
    if(n.kind==='dir'&&n.pp>.62&&zoom>.75){
      cx.fillStyle='rgba(114,136,163,'+Math.min(.85,n.pp).toFixed(2)+')';
      cx.fillText(n.label,n.px,n.py-n.rad*n.pp*zoom-7);
    }
  }
}
function hex(h,a){var n=parseInt(h.slice(1),16);
  return 'rgba('+(n>>16)+','+((n>>8)&255)+','+(n&255)+','+a.toFixed(3)+')';}

var hov=null,tip=document.getElementById('tip');
function pick(mx,my){
  var best=null,bd=1e9;
  for(var i=0;i<N.length;i++){
    var n=N[i],dx=n.px-mx,dy=n.py-my,d=dx*dx+dy*dy;
    var rr=Math.max(7,n.rad*n.pp*zoom+7);rr*=rr;
    if(d<rr&&d<bd){bd=d;best=n;}
  }
  return best;
}
function showTip(n,mx,my){
  if(!n){tip.style.display='none';hov=null;paint();return;}
  hov=n;
  document.getElementById('tp').textContent=n.id;
  document.getElementById('tt').textContent=n.label;
  var kb=n.bytes>=1024?(n.bytes/1024).toFixed(1)+' KB':n.bytes+' B';
  document.getElementById('tm').textContent=
    (n.status?n.status+'\u2003':'')+n.kind+
    (n.kind==='dir'?'':' \u00b7 '+kb)+' \u00b7 '+n.deg+
    ' edge'+(n.deg===1?'':'s');
  tip.style.display='block';
  var tw=tip.offsetWidth,th=tip.offsetHeight;
  tip.style.left=Math.max(6,Math.min(mx+15,innerWidth-tw-6))+'px';
  tip.style.top =Math.max(6,Math.min(my+15,innerHeight-th-6))+'px';
  paint();
}

var down=false,lx=0,ly=0,mv=0;
function pDown(x,y){down=true;lx=x;ly=y;mv=0;auto=false;cv.classList.add('drag');}
function pMove(x,y){
  if(down){rotY+=(x-lx)*0.0058;rotX+=(y-ly)*0.0058;
    rotX=Math.max(-1.5,Math.min(1.5,rotX));
    mv+=Math.abs(x-lx)+Math.abs(y-ly);lx=x;ly=y;paint();}
  else showTip(pick(x,y),x,y);
}
function pUp(x,y){if(down&&mv<6)showTip(pick(x,y),x,y);
  down=false;cv.classList.remove('drag');}
cv.addEventListener('mousedown',function(e){pDown(e.clientX,e.clientY);});
addEventListener('mousemove',function(e){pMove(e.clientX,e.clientY);});
addEventListener('mouseup',function(e){pUp(e.clientX,e.clientY);});
cv.addEventListener('touchstart',function(e){
  if(e.touches.length===1){var t=e.touches[0];pDown(t.clientX,t.clientY);}},{passive:true});
cv.addEventListener('touchmove',function(e){
  if(e.touches.length===1){var t=e.touches[0];pMove(t.clientX,t.clientY);}},{passive:true});
cv.addEventListener('touchend',function(e){
  var t=e.changedTouches[0];pUp(t.clientX,t.clientY);},{passive:true});
cv.addEventListener('wheel',function(e){
  e.preventDefault();auto=false;
  zoom=Math.max(.25,Math.min(7,zoom*(e.deltaY<0?1.1:.909)));paint();},{passive:false});
var pd=0;
cv.addEventListener('touchstart',function(e){
  if(e.touches.length===2){auto=false;
    pd=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,
                  e.touches[0].clientY-e.touches[1].clientY);}},{passive:true});
cv.addEventListener('touchmove',function(e){
  if(e.touches.length===2&&pd){
    var d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,
                     e.touches[0].clientY-e.touches[1].clientY);
    zoom=Math.max(.25,Math.min(7,zoom*(d/pd)));pd=d;down=false;paint();}},{passive:true});

var slow=matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
if(slow){for(var q=0;q<320;q++)tick();alpha=0;paint();}
else{(function loop(){
  var live=tick();
  if(auto)rotY+=0.00075;
  if(live||auto){paint();requestAnimationFrame(loop);}else paint();
})();}
})();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="graph_files.html")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(0 if selftest() else 1)

    root = os.path.abspath(a.root)
    p = scan_files(root)
    p["generated"] = "generated " + datetime.date.today().isoformat()

    data = json.dumps(p, separators=(",", ":")).replace("</", "<\\/")
    out = os.path.join(root, a.out)
    with open(out, "w", encoding="utf-8") as f:
        f.write(SHELL.replace("__DATA__", data))

    s = p["stats"]
    print("FILE GRAPH — measured")
    print(f"  files            {s['files']}")
    print(f"  directories      {s['dirs']}")
    print(f"  nodes            {s['nodes']}")
    print(f"  edges            {s['edges']}")
    print(f"    contains       {s['contains']}")
    print(f"    sibling        {s['sibling']}")
    print(f"    builds_on      {s['builds_on']}")
    print(f"  orphans          {s['orphans']}")
    print()
    print(f"wrote {out}  ({os.path.getsize(out)} bytes, 0 external requests)")


if __name__ == "__main__":
    main()
