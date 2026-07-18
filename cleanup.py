"""Housekeeping for Principia-Artificialis. Deletes ONLY junk artifacts
(data files, backups, mangled-paste files) — never notes, never ideas.
Moves loose scripts/notes into their homes. Prints every action."""
import os, shutil, glob
def rm(p):
    if os.path.exists(p):
        (shutil.rmtree if os.path.isdir(p) else os.remove)(p)
        print("removed:", p)
def mv(src, dst):
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst); print(f"moved: {src} -> {dst}")
# junk (artifacts, not ideas)
for p in ["n40.npz","README.md.bak","main","~",
          "python generate_entanglement_breathing_gif.py"]:
    rm(p)
for p in glob.glob("python generate_*"): rm(p)
# loose files into homes
for f in glob.glob("generate_*.py"): mv(f, "scripts/"+f)
mv("push_note027.sh","scripts/push_note027.sh")
mv("note027_thought_tensor.md","research_notes/note027_thought_tensor.md")
# gitignore hardening
gi = open(".gitignore").read() if os.path.exists(".gitignore") else ""
add = [x for x in ["*.npz","*.bak","__pycache__/","*.pyc","~"] if x not in gi]
if add:
    open(".gitignore","a").write("\n"+"\n".join(add)+"\n")
    print("gitignore +=", add)
print("done — review with: git status")
