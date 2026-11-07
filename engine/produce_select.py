import json, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
history=json.loads((root/"data/history.json").read_text(encoding="utf-8"))
produced={s.casefold() for s in history.get("produced",[])}
def pending():
    for file in sorted((root/"data/drafts").glob("*.json")):
        ep=json.loads(file.read_text(encoding="utf-8"))
        if ep["athlete"].casefold() not in produced:return file,ep
    return None
choice=pending()
if choice is None:
    subprocess.run([sys.executable,str(root/"engine/generate.py")],cwd=root,check=True)
    choice=pending()
if choice is None:raise SystemExit("Sem histórias inéditas disponíveis")
file,ep=choice
out=root/"output";out.mkdir(exist_ok=True)
(out/"selected.json").write_text(json.dumps(ep,ensure_ascii=False,indent=2),encoding="utf-8")
print("Selecionado:",ep["athlete"],file)
