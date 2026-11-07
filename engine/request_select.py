#!/usr/bin/env python3
"""Escolhe modo do pedido com base no evento GitHub sem avaliar entrada como shell."""
import json, os, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
mode="auto"
if os.environ.get("GITHUB_EVENT_NAME")=="issues":
    event=json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    body=str(event.get("issue",{}).get("body") or "")
    if any(line.lstrip().upper().startswith("LINK:") for line in body.splitlines()):
        mode="link"
print("Modo do pedido:",mode,flush=True)
script="engine/from_link.py" if mode=="link" else "engine/produce_select.py"
subprocess.run([sys.executable,str(root/script)],check=True,cwd=root)
