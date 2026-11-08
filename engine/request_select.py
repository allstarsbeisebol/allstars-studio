#!/usr/bin/env python3
"""Despacha pedidos do ALLSTARS por assunto/link sem trocar histórias."""
import json,os,subprocess,sys
from pathlib import Path
from content_request import parse
root=Path(__file__).resolve().parents[1]
req={"mode":"auto","content_type":"auto","subject":"","url":"","urls":[],"reference_text":""}
if os.environ.get("GITHUB_EVENT_NAME")=="issues":
    event=json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    req=parse(event.get("issue",{}).get("body",""))
if req["urls"] or req["reference_text"]:
    script="engine/from_link.py"
elif req["subject"]:
    script="engine/topic_generate.py"
else:
    script="engine/produce_select.py"
print("Modo:",req["mode"],"| tipo:",req["content_type"],"| assunto:",req["subject"][:100],flush=True)
subprocess.run([sys.executable,str(root/script)],check=True,cwd=root)

# Toda nova execução produz arte exclusiva, mesmo com história automática da fila.
selection=root/"output/selected.json"
if selection.is_file():
    episode=json.loads(selection.read_text(encoding="utf-8"))
    episode["unique_art_required"]=True
    if not str(episode.get("hook") or "").strip():
        # Episódios antigos da biblioteca não têm campo de hook: reutilizar
        # primeira frase existente, sem inventar novos fatos.
        import re
        narration=str(episode.get("narration") or "").strip()
        first=re.split(r"(?<=[.!?])\\s+",narration,maxsplit=1)[0].strip()
        episode["hook"]=" ".join(first.split()[:16]) or str(episode.get("title") or "")
    selection.write_text(json.dumps(episode,ensure_ascii=False,indent=2),encoding="utf-8")
