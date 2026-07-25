#!/usr/bin/env python3
"""
build_graph.py — extract the REAL link graph of the note series and emit a
single self-contained HTML renderer with the data embedded.

Why data is embedded rather than fetched: opening a local file via file://
blocks fetch() on Android Chrome and Samsung Internet. Embedding makes the
output work offline with no server and no CDN.

Edge sources, in order of authority:
  1. [[wikilinks]] that resolve to a known note number   (Obsidian-native)
  2. **Builds on:** header fields referencing #NNN        (prose-native)

Anti-vacuity control: --selftest runs the extractor against a synthetic vault
with a known-zero edge count and a known-nonzero edge count, and asserts both.
An extractor that can only ever report edges is not an instrument.

Usage:
    python scripts/build_graph.py            # writes graph.html at repo root
    python scripts/build_graph.py --selftest # prove the instrument can return null
"""

import argparse
import collections
import glob
import json
import os
import re
import sys
import tempfile

NOTE_DIRS = ("research_notes", "notes")
NUM_RE = re.compile(r"^(?:note)?(\d{3})_")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
BUILDS_ON_RE = re.compile(r"^\*\*Builds on:\*\*(.+?)(?:\n\n|\n\*\*|\n#)", re.M | re.S)
HASHNUM_RE = re.compile(r"#(\d{2,3})")
TITLE_RE = re.compile(r"^#\s+(.+)$", re.M)
STATUS_RE = re.compile(r"^\*\*Status:\*\*\s*(.+?)(?:\s*\|\s*\*\*|$)", re.M)
AUTHOR_RE = re.compile(r"^\*\*Author:\*\*\s*(.+?)(?:\s*\|\s*\*\*|$)", re.M)


def note_number(path):
    m = NUM_RE.match(os.path.basename(path))
    return m.group(1) if m else None


def classify(status):
    """Map a free-text status label onto a small set of render classes.

    Order matters: 'refuted' is checked first because a refuted claim inside an
    otherwise-Draft note is the most important fact about that note.
    """
    s = (status or "").lower()
    if "refut" in s or "failed" in s:
        return "refuted"
    if "verified" in s or "self-tested" in s:
        return "verified"
    if "speculat" in s or "freestyle" in s or "conceiv" in s or "conception" in s:
        return "speculative"
    if s:
        return "draft"
    return "unlabeled"


def scan(root):
    """Return (nodes, edges, unindexed) for a repo root."""
    files = []
    for d in NOTE_DIRS:
        files.extend(sorted(glob.glob(os.path.join(root, d, "*.md"))))

    by_num = collections.defaultdict(list)
    unindexed = []
    for f in files:
        n = note_number(f)
        if n:
            by_num[n].append(f)
        else:
            unindexed.append(os.path.relpath(f, root))

    nodes = {}
    edges = set()

    for num, paths in sorted(by_num.items()):
        for path in paths:
            txt = open(path, encoding="utf-8", errors="replace").read()
            tm = TITLE_RE.search(txt)
            sm = STATUS_RE.search(txt)
            am = AUTHOR_RE.search(txt)
            rel = os.path.relpath(path, root)

            title = (tm.group(1) if tm else os.path.basename(path)).strip()
            title = re.sub(r"^(Research\s+)?Note\s*#?\d+\s*[—:-]?\s*", "", title).strip()
            status = (sm.group(1) if sm else "").strip().rstrip("|").strip()

            key = rel  # a file, not a number — collisions must stay distinguishable
            nodes[key] = {
                "id": key,
                "num": num,
                "title": title or os.path.basename(path),
                "status": status,
                "cls": classify(status),
                "author": (am.group(1) if am else "").strip().rstrip("|").strip(),
                "stray": rel.startswith("notes" + os.sep) or rel.startswith("notes/"),
                "bytes": len(txt),
            }

            # --- edge source 1: resolvable wikilinks ---
            for raw in WIKILINK_RE.findall(txt):
                m = HASHNUM_RE.search(raw) or re.match(r"^\s*(\d{3})\b", raw)
                if not m:
                    continue  # [[links]] and [[5,1,3]] are not links
                tgt = m.group(1).zfill(3)
                if tgt in by_num and tgt != num:
                    edges.add((key, tgt, "wikilink"))

            # --- edge source 2: Builds on: prose references ---
            bm = BUILDS_ON_RE.search(txt)
            if bm:
                for r in HASHNUM_RE.findall(bm.group(1)):
                    tgt = r.zfill(3)
                    if tgt in by_num and tgt != num:
                        edges.add((key, tgt, "builds_on"))

    # resolve number-targets to a concrete file (first claimant of that number)
    first = {n: os.path.relpath(p[0], root) for n, p in by_num.items()}
    resolved = []
    seen = set()
    for src, tgt_num, kind in edges:
        tgt = first.get(tgt_num)
        if not tgt or tgt == src:
            continue
        sig = (src, tgt)
        if sig in seen:
            continue
        seen.add(sig)
        resolved.append({"source": src, "target": tgt, "kind": kind})

    return nodes, resolved, unindexed, by_num



# ---------------------------------------------------------------- file graph
FILE_NUM_RE = re.compile(r"(?:^|/)(?:note)?0*(\d{2,3})[_.]")
SKIP_DIRS = (".git", "__pycache__", ".github")

KIND_BY_EXT = {
    ".md": "doc", ".py": "code", ".sh": "code", ".thy": "proof",
    ".png": "figure", ".gif": "figure", ".svg": "figure", ".mmd": "figure",
    ".json": "data", ".csv": "data", ".npy": "data", ".log": "data",
    ".bib": "data", ".cff": "data", ".txt": "data", ".html": "build",
}


def scan_files(root):
    """Every tracked file is a node. Edges are REAL relations only:
      contains  — directory holds file       (structural, always true)
      sibling   — same note number, different file (naming convention)
      builds_on — note header reference      (prose citation)
    No edge is invented to make the picture denser.
    """
    paths = []
    for base, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in fs:
            rel = os.path.relpath(os.path.join(base, f), root)
            if rel.startswith(".") or "/." in rel:
                continue
            paths.append(rel.replace("\\", "/"))

    nodes = {}
    dirs_seen = set()
    for p in paths:
        d = os.path.dirname(p) or "/"
        dirs_seen.add(d)

    for d in sorted(dirs_seen):
        nodes[d] = {"id": d, "label": d if d != "/" else "(root)", "kind": "dir",
                    "num": None, "status": "", "cls": "dir", "bytes": 0}

    for p in paths:
        ext = os.path.splitext(p)[1].lower()
        kind = KIND_BY_EXT.get(ext, "other")
        m = FILE_NUM_RE.search("/" + p)
        num = m.group(1).zfill(3) if m else None
        status, cls = "", kind
        if ext == ".md":
            try:
                txt = open(os.path.join(root, p), encoding="utf-8", errors="replace").read()
                sm = STATUS_RE.search(txt)
                status = (sm.group(1) if sm else "").strip().rstrip("|").strip()
                if status:
                    cls = classify(status)
            except OSError:
                pass
        try:
            sz = os.path.getsize(os.path.join(root, p))
        except OSError:
            sz = 0
        nodes[p] = {"id": p, "label": os.path.basename(p), "kind": kind,
                    "num": num, "status": status, "cls": cls, "bytes": sz}

    edges = []
    seen = set()

    def add(a, b, k):
        if a == b or a not in nodes or b not in nodes:
            return
        sig = tuple(sorted((a, b))) + (k,)
        if sig in seen:
            return
        seen.add(sig)
        edges.append({"source": a, "target": b, "kind": k})

    # containment
    for p in paths:
        add(os.path.dirname(p) or "/", p, "contains")
    for d in sorted(dirs_seen):
        parent = os.path.dirname(d)
        if d != "/" and parent != d:
            add(parent or "/", d, "contains")

    # siblings by note number
    bynum = collections.defaultdict(list)
    for p in paths:
        m = FILE_NUM_RE.search("/" + p)
        if m:
            bynum[m.group(1).zfill(3)].append(p)
    for num, group in bynum.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                add(group[i], group[j], "sibling")

    # builds_on, resolved onto the note files themselves
    note_paths = [p for p in paths if p.startswith(("research_notes/", "notes/")) and p.endswith(".md")]
    first = {}
    for p in note_paths:
        m = NUM_RE.match(os.path.basename(p))
        if m:
            first.setdefault(m.group(1), p)
    for p in note_paths:
        try:
            txt = open(os.path.join(root, p), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        bm = BUILDS_ON_RE.search(txt)
        if not bm:
            continue
        for r in HASHNUM_RE.findall(bm.group(1)):
            t = first.get(r.zfill(3))
            if t:
                add(p, t, "builds_on")

    deg = collections.Counter()
    for e in edges:
        deg[e["source"]] += 1
        deg[e["target"]] += 1
    for k, n in nodes.items():
        n["deg"] = deg.get(k, 0)
        n["orphan"] = deg.get(k, 0) == 0

    kinds = collections.Counter(n["kind"] for n in nodes.values())
    ekinds = collections.Counter(e["kind"] for e in edges)
    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "stats": {
            "files": len(paths), "dirs": len(dirs_seen), "nodes": len(nodes),
            "edges": len(edges),
            "contains": ekinds.get("contains", 0),
            "sibling": ekinds.get("sibling", 0),
            "builds_on": ekinds.get("builds_on", 0),
            "orphans": sum(1 for n in nodes.values() if n["orphan"]),
        },
        "kinds": dict(kinds),
    }


def build_payload(root):
    nodes, edges, unindexed, by_num = scan(root)

    deg = collections.Counter()
    indeg = collections.Counter()
    for e in edges:
        deg[e["source"]] += 1
        deg[e["target"]] += 1
        indeg[e["target"]] += 1

    for k, n in nodes.items():
        n["deg"] = deg.get(k, 0)
        n["indeg"] = indeg.get(k, 0)
        n["orphan"] = deg.get(k, 0) == 0

    collisions = {n: [os.path.basename(p) for p in ps]
                  for n, ps in by_num.items() if len(ps) > 1}

    orphans = sorted([n for n in nodes.values() if n["orphan"]],
                     key=lambda n: n["num"])

    # candidate edges: notes sharing a number are usually topically adjacent
    candidates = []
    for num, names in sorted(collisions.items()):
        candidates.append({"num": num, "files": names})

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "stats": {
            "note_files": len(nodes),
            "numbered": len(by_num),
            "edges": len(edges),
            "wikilink_edges": sum(1 for e in edges if e["kind"] == "wikilink"),
            "buildson_edges": sum(1 for e in edges if e["kind"] == "builds_on"),
            "connected": len([n for n in nodes.values() if not n["orphan"]]),
            "orphans": len(orphans),
            "unindexed": len(unindexed),
            "collisions": len(collisions),
        },
        "orphans": [{"num": n["num"], "title": n["title"], "id": n["id"]} for n in orphans],
        "candidates": candidates,
        "unindexed": unindexed,
    }


def selftest():
    """Anti-vacuity: the extractor must be able to report ZERO edges."""
    print("=" * 62)
    print("build_graph.py — ANTI-VACUITY SELF-TEST")
    print("=" * 62)
    ok = 0
    total = 0

    with tempfile.TemporaryDirectory(dir=os.path.expanduser("~")) as d:
        rn = os.path.join(d, "research_notes")
        os.makedirs(rn)

        # Case 1: two notes, no links anywhere -> MUST be 0 edges
        open(os.path.join(rn, "001_alpha.md"), "w").write(
            "# Note #001 — Alpha\n**Status:** Draft\n\nNo links here.\n")
        open(os.path.join(rn, "002_beta.md"), "w").write(
            "# Note #002 — Beta\n**Status:** Draft\n\nAlso nothing.\n")
        p = build_payload(d)
        total += 1
        if p["stats"]["edges"] == 0 and p["stats"]["orphans"] == 2:
            print("[PASS] null case: 0 edges, 2 orphans  (expected 0 / 2)")
            ok += 1
        else:
            print(f"[FAIL] null case: {p['stats']['edges']} edges, "
                  f"{p['stats']['orphans']} orphans  (expected 0 / 2)")

        # Case 2: decoys that must NOT become edges
        open(os.path.join(rn, "003_decoy.md"), "w").write(
            "# Note #003 — Decoy\n**Status:** Draft\n\n"
            "Discussion of [[links]] and the [[5,1,3]] code. Also #999 is unknown.\n")
        p = build_payload(d)
        total += 1
        if p["stats"]["edges"] == 0:
            print("[PASS] decoy case: [[links]], [[5,1,3]], #999 -> 0 edges")
            ok += 1
        else:
            print(f"[FAIL] decoy case: {p['stats']['edges']} edges (expected 0)")

        # Case 3: a real Builds on: reference MUST produce exactly 1 edge
        open(os.path.join(rn, "004_real.md"), "w").write(
            "# Note #004 — Real\n**Status:** Draft\n"
            "**Builds on:** #001 (alpha)\n\nBody.\n")
        p = build_payload(d)
        total += 1
        if p["stats"]["edges"] == 1 and p["stats"]["buildson_edges"] == 1:
            print("[PASS] positive case: Builds on #001 -> 1 edge")
            ok += 1
        else:
            print(f"[FAIL] positive case: {p['stats']['edges']} edges (expected 1)")

        # Case 4: refuted classification must win over Draft
        total += 1
        if classify("Draft — R4 REFUTED and kept") == "refuted":
            print("[PASS] refuted label outranks Draft in classification")
            ok += 1
        else:
            print("[FAIL] refuted label misclassified")

    print()
    print(f"RESULT: {ok}/{total} checks passed")
    print("=" * 62)
    return ok == total


HTML_SHELL = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Principia Artificialis — Note Graph</title>
<style>
  :root{
    --ink:#0B0E14; --plate:#11161F; --rule:#1E2733; --rule-hi:#2B3846;
    --text:#C8D4E3; --dim:#6B7C93; --faint:#3E4A5C;
    --refuted:#E8913A; --verified:#4FB8A0; --draft:#7E8FA6; --spec:#5C6B85;
    --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
    --serif:Georgia,"Iowan Old Style","Palatino Linotype",serif;
  }
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{height:100%;background:var(--ink);color:var(--text);
    font-family:var(--mono);overflow:hidden;-webkit-text-size-adjust:100%}
  #stage{position:fixed;inset:0}
  canvas{display:block;width:100%;height:100%;touch-action:none}

  .plate{position:fixed;background:var(--plate);border:1px solid var(--rule)}

  #rail{top:0;left:0;bottom:0;width:288px;border-width:0 1px 0 0;
    padding:22px 20px;overflow-y:auto;z-index:10}
  #rail h1{font-family:var(--serif);font-size:21px;font-weight:400;
    line-height:1.15;letter-spacing:-.01em;margin-bottom:2px}
  #rail h1 em{font-style:italic;color:var(--dim)}
  .sub{font-size:10px;color:var(--faint);letter-spacing:.14em;
    text-transform:uppercase;margin-bottom:24px}

  .block{margin-bottom:22px}
  .block-h{font-size:9px;letter-spacing:.16em;text-transform:uppercase;
    color:var(--faint);padding-bottom:7px;margin-bottom:9px;
    border-bottom:1px solid var(--rule)}
  .row{display:flex;justify-content:space-between;align-items:baseline;
    font-size:12px;padding:3px 0;color:var(--dim)}
  .row b{color:var(--text);font-weight:500;font-variant-numeric:tabular-nums}

  /* the signature element: the null report */
  #null{border-left:2px solid var(--refuted);padding:12px 14px;
    background:rgba(232,145,58,.05);margin-bottom:22px}
  #null .big{font-family:var(--serif);font-size:32px;line-height:1;
    color:var(--refuted);font-variant-numeric:tabular-nums}
  #null .lbl{font-size:10px;letter-spacing:.1em;text-transform:uppercase;
    color:var(--dim);margin-top:5px;line-height:1.5}

  .key{display:flex;align-items:center;gap:8px;font-size:11px;
    color:var(--dim);padding:3px 0}
  .sw{width:9px;height:9px;border-radius:50%;flex:none}
  .sw.hollow{background:transparent;border:1px solid var(--faint)}

  .cand{font-size:11px;color:var(--dim);padding:5px 0;
    border-bottom:1px solid var(--rule);line-height:1.45}
  .cand b{color:var(--refuted);font-weight:500}

  #tip{display:none;max-width:300px;padding:13px 15px;z-index:30;
    border-color:var(--rule-hi);pointer-events:none}
  #tip .n{font-size:9px;letter-spacing:.16em;color:var(--faint);
    text-transform:uppercase}
  #tip .t{font-family:var(--serif);font-size:15px;line-height:1.3;
    margin:4px 0 8px}
  #tip .m{font-size:11px;color:var(--dim);line-height:1.55}
  #tip .m span{color:var(--text)}

  #foot{position:fixed;left:288px;right:0;bottom:0;padding:9px 18px;
    font-size:10px;color:var(--faint);letter-spacing:.05em;
    background:linear-gradient(transparent,var(--ink) 60%);z-index:5}

  @media(max-width:760px){
    #rail{width:100%;height:auto;bottom:auto;max-height:47vh;
      border-width:0 0 1px 0}
    #foot{left:0}
  }
  @media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
</head>
<body>
<div id="stage"><canvas id="c"></canvas></div>

<aside class="plate" id="rail">
  <h1>Note Graph<br><em>Principia Artificialis</em></h1>
  <div class="sub" id="gen"></div>

  <div id="null">
    <div class="big" id="orphN">—</div>
    <div class="lbl">notes with no edge<br>in either direction</div>
  </div>

  <div class="block">
    <div class="block-h">Measured</div>
    <div class="row"><span>note files</span><b id="s-files">—</b></div>
    <div class="row"><span>distinct numbers</span><b id="s-num">—</b></div>
    <div class="row"><span>edges recovered</span><b id="s-edges">—</b></div>
    <div class="row"><span>&nbsp;&nbsp;from wikilinks</span><b id="s-wl">—</b></div>
    <div class="row"><span>&nbsp;&nbsp;from Builds&nbsp;on:</span><b id="s-bo">—</b></div>
    <div class="row"><span>connected notes</span><b id="s-conn">—</b></div>
    <div class="row"><span>number collisions</span><b id="s-coll">—</b></div>
    <div class="row"><span>unindexed files</span><b id="s-unx">—</b></div>
  </div>

  <div class="block">
    <div class="block-h">Status</div>
    <div class="key"><span class="sw" style="background:var(--refuted)"></span>refuted, kept</div>
    <div class="key"><span class="sw" style="background:var(--verified)"></span>verified</div>
    <div class="key"><span class="sw" style="background:var(--draft)"></span>draft</div>
    <div class="key"><span class="sw" style="background:var(--spec)"></span>speculative</div>
    <div class="key"><span class="sw hollow"></span>orphan — no edge</div>
  </div>

  <div class="block">
    <div class="block-h">Candidate edges — shared numbers</div>
    <div id="cands"></div>
  </div>
</aside>

<div class="plate" id="tip">
  <div class="n" id="tip-n"></div>
  <div class="t" id="tip-t"></div>
  <div class="m" id="tip-m"></div>
</div>

<div id="foot">Drag to pan · scroll or pinch to zoom · tap a node.
  Edges are measured from the files, not drawn for effect.</div>

<script id="graph-data" type="application/json">__DATA__</script>
<script>
(function(){
  "use strict";
  var D = JSON.parse(document.getElementById('graph-data').textContent);
  var S = D.stats;

  function set(id,v){var e=document.getElementById(id); if(e) e.textContent=v;}
  set('gen', D.generated || '');
  set('orphN', S.orphans);
  set('s-files',S.note_files); set('s-num',S.numbered);
  set('s-edges',S.edges); set('s-wl',S.wikilink_edges);
  set('s-bo',S.buildson_edges); set('s-conn',S.connected);
  set('s-coll',S.collisions); set('s-unx',S.unindexed);

  var cw=document.getElementById('cands');
  (D.candidates||[]).forEach(function(c){
    var d=document.createElement('div'); d.className='cand';
    d.innerHTML='<b>#'+c.num+'</b> '+c.files.map(function(f){
      return f.replace(/\.md$/,'');}).join('  ·  ');
    cw.appendChild(d);
  });
  if(!(D.candidates||[]).length){
    cw.innerHTML='<div class="cand">none — no shared numbers</div>';
  }

  var CLS={refuted:'#E8913A',verified:'#4FB8A0',draft:'#7E8FA6',
           speculative:'#5C6B85',unlabeled:'#3E4A5C'};

  var cvs=document.getElementById('c'), ctx=cvs.getContext('2d'), DPR=1;
  var N=D.nodes.map(function(n){return Object.assign({},n);});
  var idx={}; N.forEach(function(n,i){idx[n.id]=i;});
  var E=D.edges.filter(function(e){
    return idx[e.source]!==undefined && idx[e.target]!==undefined;
  }).map(function(e){return {s:idx[e.source],t:idx[e.target],k:e.kind};});

  // seed: connected core in the middle, orphans on a wide outer ring so the
  // separation is legible rather than decorative
  var core=0; N.forEach(function(n){if(!n.orphan)core++;});
  var ci=0, oi=0;
  N.forEach(function(n){
    if(n.orphan){
      var a=(oi++/Math.max(1,S.orphans))*Math.PI*2;
      n.x=Math.cos(a)*420; n.y=Math.sin(a)*420;
    }else{
      var b=(ci++/Math.max(1,core))*Math.PI*2;
      n.x=Math.cos(b)*130+(Math.random()-.5)*30;
      n.y=Math.sin(b)*130+(Math.random()-.5)*30;
    }
    n.vx=0; n.vy=0;
    n.r=n.orphan?3.1:(4.2+Math.min(7,n.indeg*1.5));
  });

  function radius(){return 1;}
  var view={x:0,y:0,k:1}, alpha=1;

  function resize(){
    DPR=Math.min(window.devicePixelRatio||1,2);
    var w=cvs.clientWidth,h=cvs.clientHeight;
    cvs.width=Math.round(w*DPR); cvs.height=Math.round(h*DPR);
  }
  window.addEventListener('resize',function(){resize();draw();});
  resize();

  var railW = window.innerWidth>760?288:0;
  view.x=railW+(cvs.clientWidth-railW)/2; view.y=cvs.clientHeight/2;
  view.k = cvs.clientWidth<700?0.42:0.62;

  function step(){
    if(alpha<0.002) return false;
    alpha*=0.985;
    var i,j,a,b,dx,dy,d2,d,f;
    // repulsion (O(n^2) is fine at this scale and keeps the file dependency-free)
    for(i=0;i<N.length;i++){
      a=N[i];
      for(j=i+1;j<N.length;j++){
        b=N[j]; dx=b.x-a.x; dy=b.y-a.y; d2=dx*dx+dy*dy;
        if(d2<1e-5){dx=Math.random()-.5;dy=Math.random()-.5;d2=1e-5;}
        if(d2>360000) continue;
        f=1400/d2; d=Math.sqrt(d2);
        var ux=dx/d*f, uy=dy/d*f;
        a.vx-=ux; a.vy-=uy; b.vx+=ux; b.vy+=uy;
      }
    }
    // springs
    for(i=0;i<E.length;i++){
      a=N[E[i].s]; b=N[E[i].t];
      dx=b.x-a.x; dy=b.y-a.y; d=Math.sqrt(dx*dx+dy*dy)||1e-4;
      f=(d-84)*0.014;
      var sx=dx/d*f, sy=dy/d*f;
      a.vx+=sx; a.vy+=sy; b.vx-=sx; b.vy-=sy;
    }
    // gravity: orphans get a weaker pull so they stay legibly outside
    for(i=0;i<N.length;i++){
      a=N[i];
      var g=a.orphan?0.0016:0.010;
      a.vx-=a.x*g; a.vy-=a.y*g;
      a.x+=a.vx*alpha*2.1; a.y+=a.vy*alpha*2.1;
      a.vx*=0.82; a.vy*=0.82;
    }
    return true;
  }

  function draw(){
    var w=cvs.clientWidth,h=cvs.clientHeight;
    ctx.setTransform(DPR,0,0,DPR,0,0);
    ctx.clearRect(0,0,w,h);
    ctx.fillStyle='#0B0E14'; ctx.fillRect(0,0,w,h);

    // graticule — encodes that this is a measurement surface, not a sky
    ctx.strokeStyle='#151C26'; ctx.lineWidth=1;
    var gs=64*view.k;
    if(gs>16){
      ctx.beginPath();
      for(var gx=view.x%gs; gx<w; gx+=gs){ctx.moveTo(gx,0);ctx.lineTo(gx,h);}
      for(var gy=view.y%gs; gy<h; gy+=gs){ctx.moveTo(0,gy);ctx.lineTo(w,gy);}
      ctx.stroke();
    }

    ctx.save();
    ctx.translate(view.x,view.y); ctx.scale(view.k,view.k);

    // edges
    for(var i=0;i<E.length;i++){
      var a=N[E[i].s], b=N[E[i].t];
      ctx.strokeStyle = E[i].k==='wikilink' ? 'rgba(79,184,160,.42)'
                                            : 'rgba(126,143,166,.24)';
      ctx.lineWidth = (E[i].k==='wikilink'?1.5:1)/view.k;
      ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
    }

    // nodes
    for(i=0;i<N.length;i++){
      var n=N[i], col=CLS[n.cls]||CLS.unlabeled;
      ctx.beginPath(); ctx.arc(n.x,n.y,n.r,0,6.2832);
      if(n.orphan){
        ctx.strokeStyle='#3E4A5C'; ctx.lineWidth=1.1/view.k; ctx.stroke();
      }else{
        ctx.fillStyle=col; ctx.fill();
        if(n.cls==='refuted'){
          ctx.strokeStyle='rgba(232,145,58,.35)';
          ctx.lineWidth=3/view.k; ctx.stroke();
        }
      }
      if(n===hover){
        ctx.beginPath(); ctx.arc(n.x,n.y,n.r+5/view.k,0,6.2832);
        ctx.strokeStyle='#C8D4E3'; ctx.lineWidth=1.2/view.k; ctx.stroke();
      }
    }

    // labels for the hubs only — legibility over completeness
    ctx.font='500 '+(11/view.k)+'px ui-monospace,monospace';
    ctx.fillStyle='#6B7C93'; ctx.textAlign='center';
    for(i=0;i<N.length;i++){
      if(N[i].indeg>=2 && view.k>0.3){
        ctx.fillText('#'+N[i].num, N[i].x, N[i].y-N[i].r-6/view.k);
      }
    }
    ctx.restore();
  }

  var hover=null, tip=document.getElementById('tip');
  function pick(px,py){
    var x=(px-view.x)/view.k, y=(py-view.y)/view.k, best=null, bd=1e9;
    for(var i=0;i<N.length;i++){
      var dx=N[i].x-x, dy=N[i].y-y, d=dx*dx+dy*dy;
      var rr=(N[i].r+9/view.k); rr*=rr;
      if(d<rr && d<bd){bd=d;best=N[i];}
    }
    return best;
  }
  function showTip(n,px,py){
    if(!n){tip.style.display='none';hover=null;draw();return;}
    hover=n;
    document.getElementById('tip-n').textContent='NOTE #'+n.num+
      (n.stray?'  ·  STRAY notes/':'');
    document.getElementById('tip-t').textContent=n.title;
    var edgeTxt = n.orphan ? 'no edges — orphan'
      : n.deg+' edge'+(n.deg===1?'':'s')+' · '+n.indeg+' inbound';
    document.getElementById('tip-m').innerHTML=
      (n.status?'<span>'+esc(n.status)+'</span><br>':'')+
      (n.author?esc(n.author)+'<br>':'')+edgeTxt;
    tip.style.display='block';
    var tw=tip.offsetWidth, th=tip.offsetHeight;
    tip.style.left=Math.max(8,Math.min(px+16,window.innerWidth-tw-8))+'px';
    tip.style.top=Math.max(8,Math.min(py+16,window.innerHeight-th-8))+'px';
    draw();
  }
  function esc(s){return String(s).replace(/[<>&]/g,function(c){
    return {'<':'&lt;','>':'&gt;','&':'&amp;'}[c];});}

  var drag=false, lx=0, ly=0, moved=0;
  function down(x,y){drag=true;lx=x;ly=y;moved=0;}
  function move(x,y){
    if(drag){
      view.x+=x-lx; view.y+=y-ly; moved+=Math.abs(x-lx)+Math.abs(y-ly);
      lx=x;ly=y; draw();
    }else{ showTip(pick(x,y),x,y); }
  }
  function up(x,y){
    if(drag&&moved<6) showTip(pick(x,y),x,y);
    drag=false;
  }
  cvs.addEventListener('mousedown',function(e){down(e.clientX,e.clientY);});
  window.addEventListener('mousemove',function(e){move(e.clientX,e.clientY);});
  window.addEventListener('mouseup',function(e){up(e.clientX,e.clientY);});
  cvs.addEventListener('touchstart',function(e){
    var t=e.touches[0]; down(t.clientX,t.clientY);},{passive:true});
  cvs.addEventListener('touchmove',function(e){
    if(e.touches.length===1){var t=e.touches[0];move(t.clientX,t.clientY);}
    },{passive:true});
  cvs.addEventListener('touchend',function(e){
    var t=e.changedTouches[0]; up(t.clientX,t.clientY);},{passive:true});
  cvs.addEventListener('wheel',function(e){
    e.preventDefault();
    var f=e.deltaY<0?1.12:0.893;
    var nk=Math.max(0.12,Math.min(4,view.k*f));
    view.x=e.clientX-(e.clientX-view.x)*(nk/view.k);
    view.y=e.clientY-(e.clientY-view.y)*(nk/view.k);
    view.k=nk; draw();
  },{passive:false});

  var pd=0;
  cvs.addEventListener('touchstart',function(e){
    if(e.touches.length===2){
      pd=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,
                    e.touches[0].clientY-e.touches[1].clientY);
    }},{passive:true});
  cvs.addEventListener('touchmove',function(e){
    if(e.touches.length===2&&pd){
      var d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,
                       e.touches[0].clientY-e.touches[1].clientY);
      var nk=Math.max(0.12,Math.min(4,view.k*(d/pd)));
      var cx=(e.touches[0].clientX+e.touches[1].clientX)/2;
      var cy=(e.touches[0].clientY+e.touches[1].clientY)/2;
      view.x=cx-(cx-view.x)*(nk/view.k);
      view.y=cy-(cy-view.y)*(nk/view.k);
      view.k=nk; pd=d; drag=false; draw();
    }},{passive:true});

  var reduce = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce){ for(var q=0;q<260;q++) step(); alpha=0; draw(); }
  else {
    (function loop(){ if(step()){draw(); requestAnimationFrame(loop);} else draw(); })();
  }
})();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default="graph.html")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", help="also write raw graph JSON here")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(0 if selftest() else 1)

    root = os.path.abspath(a.root)
    payload = build_payload(root)

    import datetime
    payload["generated"] = "generated " + datetime.date.today().isoformat()

    data = json.dumps(payload, separators=(",", ":"))
    data = data.replace("</", "<\\/")  # keep a stray </script> out of the shell
    html = HTML_SHELL.replace("__DATA__", data)

    out = os.path.join(root, a.out)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    s = payload["stats"]
    print("MEASURED GRAPH")
    print(f"  note files              {s['note_files']}")
    print(f"  distinct numbers        {s['numbered']}")
    print(f"  edges recovered         {s['edges']}")
    print(f"    from wikilinks        {s['wikilink_edges']}")
    print(f"    from 'Builds on:'     {s['buildson_edges']}")
    print(f"  connected notes         {s['connected']}")
    print(f"  ORPHANS (no edge)       {s['orphans']}")
    print(f"  number collisions       {s['collisions']}")
    print(f"  unindexed files         {s['unindexed']}")
    print()
    print(f"wrote {out}  ({os.path.getsize(out)} bytes, 0 external requests)")

    if a.json:
        with open(os.path.join(root, a.json), "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"wrote {a.json}")


if __name__ == "__main__":
    main()
