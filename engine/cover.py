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
poster(episode).save(dest,optimize=True)
print("Capa editorial ALLSTARS:",dest)
