#!/usr/bin/env python3
"""Despacha pedidos do ALLSTARS por assunto/link sem trocar histórias."""
import json,os,subprocess,sys
from pathlib import Path
from content_request import parse
root=Path(__file__).resolve().parents[1]
req={"mode":"auto","content_type":"auto","subject":"","url":""}
if os.environ.get("GITHUB_EVENT_NAME")=="issues":
    event=json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    req=parse(event.get("issue",{}).get("body",""))
if req["url"]:
    script="engine/from_link.py"
elif req["subject"]:
    script="engine/topic_generate.py"
else:
    script="engine/produce_select.py"
print("Modo:",req["mode"],"| tipo:",req["content_type"],"| assunto:",req["subject"][:100],flush=True)
subprocess.run([sys.executable,str(root/script)],check=True,cwd=root)
