#!/usr/bin/env python3
"""Seleciona o episódio existente sem editar arquivos manualmente."""
import json, os, shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=os.environ.get("EPISODE_SOURCE","ultimo-rascunho")
if source=="ultimo-rascunho":
    drafts=sorted((root/"data/drafts").glob("*.json"))
    if not drafts:raise SystemExit("Ainda não há rascunhos. Execute primeiro Novo rascunho semanal.")
    chosen=drafts[-1]
elif source=="episodio-principal":
    chosen=root/"data/episode.json"
else:
    raise SystemExit("Fonte de episódio inválida")
episode=json.loads(chosen.read_text(encoding="utf-8"))
if not isinstance(episode.get("sources"),list) or not episode["sources"]:
    raise SystemExit("Não há fontes cadastradas para o episódio.")
if len(episode.get("narration","").split())<50:
    raise SystemExit("A narração está curta demais. Revise antes de produzir.")
out=root/"output/selected.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(episode,ensure_ascii=False,indent=2),encoding="utf-8")
print("Episódio selecionado:",chosen,"—",episode.get("athlete"))
print("IMPORTANTE: seleção não substitui revisão factual nem conferência de licenças.")
