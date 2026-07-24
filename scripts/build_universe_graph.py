#!/usr/bin/env python3
"""
build_universe_graph.py
-----------------------
Builds a single self-contained HTML that contains:
  - Every file from every holland202 public repo as a node
  - The measured contains / sibling / builds_on edges from Principia
  - Edge-nodes (each relationship becomes a first-class node you can hover)

Usage:
  python scripts/build_universe_graph.py
  # writes universe.html

Then open universe.html or push it and point the Living Graph tab at it.
"""

import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict

# ------------------------------------------------------------------
# 1. Hard-coded list of your public repos (expand as needed)
# ------------------------------------------------------------------
REPOS = [
    "Principia-Artificialis",
    "qsleuth",
    "polytope-explorer",
    "qolas-synthesis",
    "quasar",
    "sovereign-evolution",
    "slc-v12-",
    "edge-ai-primitives",
    "skn-v1-",
    "coverage-preserving-synthesis",
    "sentinel-batadal-validation",
    "sovereign-suite",
]

# ------------------------------------------------------------------
# 2. Helper to turn a path into a stable node id
# ------------------------------------------------------------------
def nid(repo, path=""):
    if path:
        return f"{repo}/{path}"
    return repo

# ------------------------------------------------------------------
# 3. Build the node & edge lists
# ------------------------------------------------------------------
nodes = []
edges = []
seen = set()

def add_node(id_, label, kind, repo, bytes_=0, status="", cls=None):
    if id_ in seen:
        return
    seen.add(id_)
    nodes.append({
        "id": id_,
        "label": label,
        "kind": kind,
        "repo": repo,
        "bytes": bytes_,
        "status": status,
        "cls": cls or kind,
        "deg": 0,
        "orphan": False,
    })

def add_edge(src, tgt, kind):
    edges.append({"source": src, "target": tgt, "kind": kind})

# ---- root node for the whole universe
add_node("universe", "holland202 universe", "dir", "meta")

# ---- one node per repo
for repo in REPOS:
    rid = nid(repo)
    add_node(rid, repo, "dir", repo)
    add_edge("universe", rid, "contains")

# ------------------------------------------------------------------
# 4. Inject the full Principia measured graph (the one you already have)
#    We treat it as the richest source of sibling / builds_on edges.
# ------------------------------------------------------------------
# You can paste the full nodes/edges JSON from your existing graph_data
# or from the HTML <script id="D"> here if you want the exact 380 edges.
# For now we keep a lightweight skeleton so the script is self-contained.

# Example skeleton – replace with the real list when you run locally
principia_files = [
    "README.md", "WHITEPAPER.md", "START_HERE.md",
    "research_notes/note043_free_energy_of_reasoning.md",
    "research_notes/note048_the_governor_is_the_dynamics.md",
    "scripts/build_filegraph.py", "scripts/build_graph.py",
]
for p in principia_files:
    pid = nid("Principia-Artificialis", p)
    kind = "doc" if p.endswith(".md") else "code"
    add_node(pid, Path(p).name, kind, "Principia-Artificialis")
    add_edge(nid("Principia-Artificialis"), pid, "contains")

# ------------------------------------------------------------------
# 5. Edge-nodes (make every relationship a first-class citizen)
# ------------------------------------------------------------------
edge_nodes = []
for i, e in enumerate(edges):
    eid = f"edge:{e['kind']}:{i}"
    edge_nodes.append({
        "id": eid,
        "label": f"{e['kind']}",
        "kind": "edge",
        "repo": "meta",
        "bytes": 0,
        "status": "",
        "cls": "edge",
        "deg": 2,
        "orphan": False,
        "src": e["source"],
        "tgt": e["target"],
    })
    # connect the edge-node to its two endpoints
    add_edge(e["source"], eid, "has_edge")
    add_edge(eid, e["target"], "has_edge")

nodes.extend(edge_nodes)

# ------------------------------------------------------------------
# 6. Simple degree calculation
# ------------------------------------------------------------------
deg = defaultdict(int)
for e in edges:
    deg[e["source"]] += 1
    deg[e["target"]] += 1
for n in nodes:
    n["deg"] = deg.get(n["id"], 0)

# ------------------------------------------------------------------
# 7. Emit the self-contained HTML (same style as your original graph)
# ------------------------------------------------------------------
stats = {
    "files": sum(1 for n in nodes if n["kind"] not in ("dir", "edge")),
    "dirs": sum(1 for n in nodes if n["kind"] == "dir"),
    "nodes": len(nodes),
    "edges": len(edges),
    "contains": sum(1 for e in edges if e["kind"] == "contains"),
    "sibling": sum(1 for e in edges if e["kind"] == "sibling"),
    "builds_on": sum(1 for e in edges if e["kind"] == "builds_on"),
    "orphans": 0,
}

payload = {
    "nodes": nodes,
    "edges": edges,
    "stats": stats,
    "kinds": {},
    "generated": "universe graph generated by build_universe_graph.py",
}

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Universe Graph — holland202 Second Brain</title>
<style>
  :root{{
    --void:#05070C; --panel:#0C1119; --rule:#1A2431; --text:#D6E2F0;
    --dim:#7288A3; --faint:#3D4C60; --hot:#FFB454;
    --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
    --serif:Georgia,"Iowan Old Style",serif;
  }}
  *{{margin:0;padding:0;box-sizing:border-box}}
  html,body{{height:100%;background:var(--void);color:var(--text);
    font-family:var(--mono);overflow:hidden;-webkit-text-size-adjust:100%}}
  canvas{{display:block;width:100vw;height:100vh;touch-action:none;cursor:grab}}
  canvas.drag{{cursor:grabbing}}
  .panel{{position:fixed;background:rgba(12,17,25,.93);border:1px solid var(--rule)}}
  #hud{{top:0;left:0;bottom:0;width:270px;border-width:0 1px 0 0;
    padding:20px 18px;overflow-y:auto;z-index:10}}
  #hud h1{{font-family:var(--serif);font-size:19px;font-weight:400;line-height:1.15}}
  #hud h1 em{{font-style:italic;color:var(--dim);display:block;font-size:15px}}
  .stamp{{font-size:9px;letter-spacing:.16em;text-transform:uppercase;
    color:var(--faint);margin:6px 0 20px}}
  .hero{{border-left:2px solid var(--hot);padding:11px 13px;
    background:rgba(255,180,84,.05);margin-bottom:20px}}
  .hero .n{{font-family:var(--serif);font-size:34px;line-height:1;color:var(--hot);
    font-variant-numeric:tabular-nums}}
  .hero .l{{font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;
    color:var(--dim);margin-top:4px;line-height:1.5}}
  .sec{{font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:var(--faint);
    padding-bottom:6px;margin:0 0 8px;border-bottom:1px solid var(--rule)}}
  .grp{{margin-bottom:20px}}
  .r{{display:flex;justify-content:space-between;font-size:11.5px;
    padding:2.5px 0;color:var(--dim)}}
  .r b{{color:var(--text);font-weight:500;font-variant-numeric:tabular-nums}}
  .k{{display:flex;align-items:center;gap:8px;font-size:11px;color:var(--dim);padding:2.5px 0}}
  .d{{width:8px;height:8px;border-radius:50%;flex:none;box-shadow:0 0 7px currentColor}}
  #tip{{display:none;max-width:290px;padding:12px 14px;z-index:30;pointer-events:none}}
  #tip .p{{font-size:9px;letter-spacing:.13em;color:var(--faint);
    text-transform:uppercase;word-break:break-all}}
  #tip .t{{font-family:var(--serif);font-size:14.5px;line-height:1.3;margin:4px 0 7px;
    word-break:break-word}}
  #tip .m{{font-size:11px;color:var(--dim);line-height:1.55}}
  #bar{{position:fixed;left:270px;right:0;bottom:0;padding:8px 16px;font-size:10px;
    color:var(--faint);letter-spacing:.04em;z-index:5;
    background:linear-gradient(transparent,var(--void) 65%)}}
  @media(max-width:760px){{
    #hud{{width:100%;bottom:auto;max-height:44vh;border-width:0 0 1px 0}}
    #bar{{left:0}}
  }}
</style>
</head>
<body>
<canvas id="c"></canvas>
<aside class="panel" id="hud">
  <h1>Universe Graph<em>holland202 Second Brain</em></h1>
  <div class="stamp" id="stamp"></div>
  <div class="hero">
    <div class="n" id="hE">—</div>
    <div class="l">measured edges<br>+ edge-nodes</div>
  </div>
  <div class="grp">
    <div class="sec">Nodes</div>
    <div class="r"><span>files</span><b id="sF">—</b></div>
    <div class="r"><span>directories</span><b id="sD">—</b></div>
    <div class="r"><span>edge-nodes</span><b id="sE">—</b></div>
  </div>
  <div class="grp">
    <div class="sec">Edges by kind</div>
    <div class="r"><span>contains</span><b id="eC">—</b></div>
    <div class="r"><span>sibling</span><b id="eS">—</b></div>
    <div class="r"><span>builds on</span><b id="eB">—</b></div>
  </div>
  <div class="grp">
    <div class="sec">Legend</div>
    <div id="leg"></div>
  </div>
</aside>
<div class="panel" id="tip">
  <div class="p" id="tp"></div>
  <div class="t" id="tt"></div>
  <div class="m" id="tm"></div>
</div>
<div id="bar">drag to orbit · pinch/scroll to zoom · tap a node (including edge-nodes)</div>
<script id="D" type="application/json">{json.dumps(payload)}</script>
<script>
// identical force-directed 3D renderer from your original graph
(function(){{
"use strict";
var D=JSON.parse(document.getElementById('D').textContent),S=D.stats;
function T(i,v){{var e=document.getElementById(i);if(e)e.textContent=v;}}
T('stamp',D.generated||'');T('hE',S.edges);T('sF',S.files);T('sD',S.dirs);
T('sE',D.nodes.filter(n=>n.kind==='edge').length);
T('eC',S.contains);T('eS',S.sibling);T('eB',S.builds_on);

var COL={{dir:'#5B7FA8',doc:'#8FA8C4',code:'#4FD6B8',figure:'#C77DD6',
         data:'#E0C060',proof:'#FF7B6B',build:'#6B7C93',other:'#46566B',
         edge:'#FFB454',refuted:'#FFB454',verified:'#4FD6B8',draft:'#8FA8C4',
         speculative:'#6A7E9B',unlabeled:'#46566B'}};
var LEG=[['dir','directory / repo'],['doc','markdown'],['code','python / shell'],
         ['figure','figure / gif'],['edge','edge-node (relationship)']];
var lg=document.getElementById('leg');
LEG.forEach(function(p){{var d=document.createElement('div');d.className='k';
  d.innerHTML='<span class="d" style="background:'+COL[p[0]]+';color:'+COL[p[0]]+'"></span>'+p[1];
  lg.appendChild(d);}});

var N=D.nodes.map(function(n){{return Object.assign({{}},n);}});
var ix={{}};N.forEach(function(n,i){{ix[n.id]=i;}});
var E=D.edges.filter(function(e){{return ix[e.source]!==undefined&&ix[e.target]!==undefined;}})
             .map(function(e){{return {{s:ix[e.source],t:ix[e.target],k:e.kind}};}});

var _s=1337;function rnd(){{_s=(_s*1103515245+12345)&0x7fffffff;return _s/0x7fffffff;}}
N.forEach(function(n){{
  var u=rnd()*2-1,th=rnd()*6.2832,r=200*Math.cbrt(rnd())+50;
  var s=Math.sqrt(1-u*u);
  n.x=r*s*Math.cos(th);n.y=r*s*Math.sin(th);n.z=r*u;
  n.vx=n.vy=n.vz=0;
  n.m=n.kind==='dir'?3.5:(n.kind==='edge'?0.8:1);
  n.rad=n.kind==='dir'?3.8:(n.kind==='edge'?1.2:1.6);
  n.col=COL[n.cls]||COL[n.kind]||COL.other;
}});

var cv=document.getElementById('c'),cx=cv.getContext('2d'),DPR=1;
function fit(){{DPR=Math.min(devicePixelRatio||1,2);
  cv.width=Math.round(cv.clientWidth*DPR);cv.height=Math.round(cv.clientHeight*DPR);}}
addEventListener('resize',function(){{fit();paint();}});fit();

var rotY=0.4,rotX=-0.22,zoom=innerWidth<760?0.9:1.4,alpha=1,auto=true;

function tick(){{
  if(alpha<0.0025)return false;
  alpha*=0.986;
  var i,j,a,b,dx,dy,dz,d2,d,f,u;
  for(i=0;i<N.length;i++){{
    a=N[i];
    for(j=i+1;j<N.length;j++){{
      b=N[j];dx=b.x-a.x;dy=b.y-a.y;dz=b.z-a.z;d2=dx*dx+dy*dy+dz*dz;
      if(d2<1e-4){{dx=rnd()-.5;dy=rnd()-.5;dz=rnd()-.5;d2=1e-4;}}
      if(d2>300000)continue;
      d=Math.sqrt(d2);f=700*a.m*b.m/d2/d;
      a.vx-=dx*f;a.vy-=dy*f;a.vz-=dz*f;
      b.vx+=dx*f;b.vy+=dy*f;b.vz+=dz*f;
    }}
  }}
  for(i=0;i<E.length;i++){{
    a=N[E[i].s];b=N[E[i].t];
    dx=b.x-a.x;dy=b.y-a.y;dz=b.z-a.z;
    d=Math.sqrt(dx*dx+dy*dy+dz*dz)||1e-4;
    u=E[i].k==='contains'?50:(E[i].k==='sibling'?30:40);
    f=(d-u)*0.018/d;
    a.vx+=dx*f;a.vy+=dy*f;a.vz+=dz*f;
    b.vx-=dx*f;b.vy-=dy*f;b.vz-=dz*f;
  }}
  for(i=0;i<N.length;i++){{
    a=N[i];
    a.vx-=a.x*0.006;a.vy-=a.y*0.006;a.vz-=a.z*0.006;
    a.x+=a.vx*alpha*1.6;a.y+=a.vy*alpha*1.6;a.z+=a.vz*alpha*1.6;
    a.vx*=0.82;a.vy*=0.82;a.vz*=0.82;
  }}
  return true;
}}

var W,H,CXp,CYp;
function proj(n){{
  var cy=Math.cos(rotY),sy=Math.sin(rotY),cxr=Math.cos(rotX),sxr=Math.sin(rotX);
  var x=n.x*cy-n.z*sy, z=n.x*sy+n.z*cy;
  var y=n.y*cxr-z*sxr;  z=n.y*sxr+z*cxr;
  var p=760/(760+z+420);
  n.px=CXp+x*p*zoom; n.py=CYp+y*p*zoom; n.pz=z; n.pp=p;
}}

function paint(){{
  W=cv.clientWidth;H=cv.clientHeight;CXp=W/2+(W>760?135:0);CYp=H/2;
  cx.setTransform(DPR,0,0,DPR,0,0);
  cx.globalCompositeOperation='source-over';
  var g=cx.createRadialGradient(CXp,CYp,0,CXp,CYp,Math.max(W,H)*.78);
  g.addColorStop(0,'#0B1220');g.addColorStop(1,'#05070C');
  cx.fillStyle=g;cx.fillRect(0,0,W,H);

  var i,n;
  for(i=0;i<N.length;i++)proj(N[i]);

  cx.globalCompositeOperation='lighter';
  for(i=0;i<E.length;i++){{
    var a=N[E[i].s],b=N[E[i].t];
    var dep=Math.max(.08,Math.min(1,(a.pp+b.pp)/2));
    var o,c;
    if(E[i].k==='sibling'){{c='199,125,214';o=.40*dep;}}
    else if(E[i].k==='builds_on'){{c='79,214,184';o=.34*dep;}}
    else if(E[i].k==='has_edge'){{c='255,180,84';o=.25*dep;}}
    else {{c='70,92,124';o=.16*dep;}}
    cx.strokeStyle='rgba('+c+','+o.toFixed(3)+')';
    cx.lineWidth=(E[i].k==='contains'?.6:1.0)*dep;
    cx.beginPath();cx.moveTo(a.px,a.py);cx.lineTo(b.px,b.py);cx.stroke();
  }}

  var ord=N.slice().sort(function(p,q){{return q.pz-p.pz;}});
  for(i=0;i<ord.length;i++){{
    n=ord[i];
    var r=Math.max(.6,n.rad*n.pp*zoom),dep=Math.max(.1,Math.min(1,n.pp));
    var gr=cx.createRadialGradient(n.px,n.py,0,n.px,n.py,r*6);
    gr.addColorStop(0,hex(n.col,.55*dep));
    gr.addColorStop(.4,hex(n.col,.12*dep));
    gr.addColorStop(1,hex(n.col,0));
    cx.fillStyle=gr;
    cx.beginPath();cx.arc(n.px,n.py,r*6,0,6.2832);cx.fill();
  }}
  cx.globalCompositeOperation='source-over';
  for(i=0;i<ord.length;i++){{
    n=ord[i];
    var r=Math.max(.6,n.rad*n.pp*zoom),dep=Math.max(.15,Math.min(1,n.pp));
    cx.fillStyle=hex(n.col,.55+.45*dep);
    cx.beginPath();cx.arc(n.px,n.py,r,0,6.2832);cx.fill();
    if(n===hov){{
      cx.strokeStyle='rgba(214,226,240,.9)';cx.lineWidth=1.2;
      cx.beginPath();cx.arc(n.px,n.py,r+5,0,6.2832);cx.stroke();
    }}
  }}

  cx.font='500 10px '+getComputedStyle(document.body).fontFamily;
  cx.textAlign='center';
  for(i=0;i<N.length;i++){{
    n=N[i];
    if((n.kind==='dir'||n.kind==='edge')&&n.pp>.55&&zoom>.7){{
      cx.fillStyle='rgba(114,136,163,'+Math.min(.85,n.pp).toFixed(2)+')';
      cx.fillText(n.label,n.px,n.py-n.rad*n.pp*zoom-6);
    }}
  }}
}}
function hex(h,a){{var n=parseInt(h.slice(1),16);
  return 'rgba('+(n>>16)+','+((n>>8)&255)+','+(n&255)+','+a.toFixed(3)+')';}}

var hov=null,tip=document.getElementById('tip');
function pick(mx,my){{
  var best=null,bd=1e9;
  for(var i=0;i<N.length;i++){{
    var n=N[i],dx=n.px-mx,dy=n.py-my,d=dx*dx+dy*dy;
    var rr=Math.max(6,n.rad*n.pp*zoom+6);rr*=rr;
    if(d<rr&&d<bd){{bd=d;best=n;}}
  }}
  return best;
}}
function showTip(n,mx,my){{
  if(!n){{tip.style.display='none';hov=null;paint();return;}}
  hov=n;
  document.getElementById('tp').textContent=n.id;
  document.getElementById('tt').textContent=n.label;
  document.getElementById('tm').textContent=
    (n.repo?n.repo+' \u00b7 ':'')+n.kind+' \u00b7 '+n.deg+' edge'+(n.deg===1?'':'s');
  tip.style.display='block';
  var tw=tip.offsetWidth,th=tip.offsetHeight;
  tip.style.left=Math.max(6,Math.min(mx+14,innerWidth-tw-6))+'px';
  tip.style.top =Math.max(6,Math.min(my+14,innerHeight-th-6))+'px';
  paint();
}}

var down=false,lx=0,ly=0,mv=0;
function pDown(x,y){{down=true;lx=x;ly=y;mv=0;auto=false;cv.classList.add('drag');}}
function pMove(x,y){{
  if(down){{rotY+=(x-lx)*0.0055;rotX+=(y-ly)*0.0055;
    rotX=Math.max(-1.5,Math.min(1.5,rotX));
    mv+=Math.abs(x-lx)+Math.abs(y-ly);lx=x;ly=y;paint();}}
  else showTip(pick(x,y),x,y);
}}
function pUp(x,y){{if(down&&mv<6)showTip(pick(x,y),x,y);
  down=false;cv.classList.remove('drag');}}
cv.addEventListener('mousedown',function(e){{pDown(e.clientX,e.clientY);}});
addEventListener('mousemove',function(e){{pMove(e.clientX,e.clientY);}});
addEventListener('mouseup',function(e){{pUp(e.clientX,e.clientY);}});
cv.addEventListener('touchstart',function(e){{
  if(e.touches.length===1){{var t=e.touches[0];pDown(t.clientX,t.clientY);}}}},{{passive:true}});
cv.addEventListener('touchmove',function(e){{
  if(e.touches.length===1){{var t=e.touches[0];pMove(t.clientX,t.clientY);}}}},{{passive:true}});
cv.addEventListener('touchend',function(e){{
  var t=e.changedTouches[0];pUp(t.clientX,t.clientY);}},{{passive:true}});
cv.addEventListener('wheel',function(e){{
  e.preventDefault();auto=false;
  zoom=Math.max(.2,Math.min(6,zoom*(e.deltaY<0?1.1:.91)));paint();}},{{passive:false}});

var slow=matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
if(slow){{for(var q=0;q<280;q++)tick();alpha=0;paint();}}
else{{(function loop(){{
  var live=tick();
  if(auto)rotY+=0.0007;
  if(live||auto){{paint();requestAnimationFrame(loop);}}else paint();
}})();}}
}})();
</script>
</body>
</html>
"""

with open("universe.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Wrote universe.html")
print(f"  nodes: {len(nodes)}")
print(f"  edges: {len(edges)}")
print("Open universe.html in a browser or push it and point the Living Graph tab at it.")
