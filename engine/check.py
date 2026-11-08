#!/usr/bin/env python3
"""Verificação de integridade sem dependências adicionais nem API paga."""
import json, py_compile
from pathlib import Path

root=Path(__file__).resolve().parents[1]
scripts=["engine/generate.py","engine/select_episode.py","engine/render.py","engine/speech.py","engine/produce_select.py","engine/publish_manifest.py","engine/poster.py","engine/cover.py","engine/subtitles.py","engine/commons_media.py","engine/editorial_guard.py"]
for script in scripts:
    py_compile.compile(str(root/script), doraise=True)
    print("OK Python:",script)

required=["index.html","brand/identity.json","ALLSTARS - Bíblia Visual 2026.md","data/episode.json","data/history.json",".github/workflows/weekly.yml",".github/workflows/render.yml"]
for filename in required:
    if not (root/filename).is_file():
        raise SystemExit("Arquivo obrigatório ausente: "+filename)
    print("OK Arquivo:",filename)

history=json.loads((root/"data/history.json").read_text(encoding="utf-8"))
seen=[x.strip().casefold() for x in history.get("covered",[])+history.get("drafted",[])]
if len(seen)!=len(set(seen)):
    raise SystemExit("Erro: atleta repetido no histórico.")

episodes=[root/"data/episode.json",*sorted((root/"data/drafts").glob("*.json"))]
for filename in episodes:
    d=json.loads(filename.read_text(encoding="utf-8"))
    for field in ("athlete","title","narration","caption"):
        if not isinstance(d.get(field),str) or not d[field].strip():
            raise SystemExit(f"{filename}: campo {field} vazio")
    if not isinstance(d.get("sources"),list) or not d["sources"]:
        raise SystemExit(f"{filename}: fontes ausentes")
    if not isinstance(d.get("screens"),list):
        raise SystemExit(f"{filename}: telas inválidas")
    print("OK Episódio:",filename.name)
print("TESTES DE INTEGRIDADE CONCLUÍDOS. A revisão histórica e o processamento real do áudio/vídeo são etapas separadas.")
