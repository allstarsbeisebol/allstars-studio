#!/usr/bin/env python3
"""Produz capa oficial ALLSTARS com o compositor editorial 9:16."""
import argparse,json
from pathlib import Path
from poster import poster
p=argparse.ArgumentParser()
p.add_argument("--episode",default="data/episode.json")
p.add_argument("--output",default="output/capa.png")
args=p.parse_args()
episode=json.loads(Path(args.episode).read_text(encoding="utf-8"))
dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
image=poster(episode)
image.save(dest,optimize=True)
# Prévia exata da grade de perfil 3:4, centralizada no Reel 9:16.
# 1080x1440 corresponde ao corte y=240..1680 da arte vertical.
preview=image.crop((0,240,1080,1680))
preview_path=dest.parent/'capa_perfil_3x4.png'
preview.save(preview_path,optimize=True)
print('Prévia de perfil 3:4:',preview_path)
print("Capa editorial ALLSTARS:",dest)
