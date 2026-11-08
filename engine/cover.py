#!/usr/bin/env python3
"""Produz capa oficial ALLSTARS com o compositor editorial 9:16."""
import argparse,json
from pathlib import Path
from poster import poster, official_logo, profile_from_cover
from anime_assets import cover_from_approved_asset
from PIL import Image, ImageDraw
p=argparse.ArgumentParser()
p.add_argument("--episode",default="data/episode.json")
p.add_argument("--output",default="output/capa.png")
args=p.parse_args()
episode=json.loads(Path(args.episode).read_text(encoding="utf-8"))
dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
curated=cover_from_approved_asset(episode) if not episode.get("unique_art_required") else None
image=curated[0] if curated is not None else poster(episode)
if curated is not None:
    # A arte aprovada é uma composição completa. Preserve a ilustração
    # e a manchete; substitua somente a região de marca pela logo OFICIAL.
    image=image.convert("RGBA")
    stamp=Image.new("RGBA",image.size,(0,0,0,0))
    draw=ImageDraw.Draw(stamp,"RGBA")
    draw.rectangle((0,1655,1080,1920),fill=(4,14,33,255))
    image.alpha_composite(stamp)
    mark=official_logo()
    scale=min((440 if mark.width>=500 else 220)/max(1,mark.width),
              (155 if mark.width>=500 else 115)/max(1,mark.height),
              1.0 if mark.width>=500 else 1.2)
    mark=mark.resize((max(1,round(mark.width*scale)),max(1,round(mark.height*scale))),Image.Resampling.LANCZOS)
    image.alpha_composite(mark,((1080-mark.width)//2,1700+(190-mark.height)//2))
    image=image.convert("RGB")
image.save(dest,optimize=True)
print('Visual:', 'anime aprovado para este atleta' if curated is not None else 'arte gerada pelo compositor atual')
# Recorte de perfil do MESMO compositor; a marca oficial é reaplicada nítida.
preview=profile_from_cover(image)
preview_path=dest.parent/'capa_perfil_3x4.png'
preview.save(preview_path,optimize=True)
print('Prévia de perfil 3:4:',preview_path)
print("Capa editorial ALLSTARS:",dest)
