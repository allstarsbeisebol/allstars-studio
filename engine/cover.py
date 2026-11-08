#!/usr/bin/env python3
"""Produz capa oficial ALLSTARS com o compositor editorial 9:16."""
import argparse,json
from pathlib import Path
from poster import poster, official_logo
from anime_assets import cover_from_approved_asset
from PIL import Image, ImageDraw
p=argparse.ArgumentParser()
p.add_argument("--episode",default="data/episode.json")
p.add_argument("--output",default="output/capa.png")
args=p.parse_args()
episode=json.loads(Path(args.episode).read_text(encoding="utf-8"))
dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
curated=cover_from_approved_asset(episode)
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
    scale=min(510/max(1,mark.width),190/max(1,mark.height))
    mark=mark.resize((max(1,round(mark.width*scale)),max(1,round(mark.height*scale))),Image.Resampling.LANCZOS)
    image.alpha_composite(mark,((1080-mark.width)//2,1700+(190-mark.height)//2))
    image=image.convert("RGB")
image.save(dest,optimize=True)
print('Visual:', 'anime aprovado para este atleta' if curated is not None else 'arte gerada pelo compositor atual')
# Prévia exata da grade de perfil 3:4, centralizada no Reel 9:16.
# 1080x1440 corresponde ao corte y=240..1680 da arte vertical.
preview=image.crop((0,240,1080,1680)).convert('RGBA')
# No recorte 3:4, a logo do rodapé 9:16 sairia da grade.
# Reaplicamos o arquivo ORIGINAL, sem redesenho, numa faixa de proteção inferior.
bar=Image.new('RGBA',preview.size,(0,0,0,0))
ImageDraw.Draw(bar,'RGBA').rectangle((0,1300,1080,1440),fill=(4,14,33,230))
preview.alpha_composite(bar)
brand=official_logo()
brand.thumbnail((320,105),Image.Resampling.LANCZOS)
preview.alpha_composite(brand,((1080-brand.width)//2,1320))
preview=preview.convert('RGB')
preview_path=dest.parent/'capa_perfil_3x4.png'
preview.save(preview_path,optimize=True)
print('Prévia de perfil 3:4:',preview_path)
print("Capa editorial ALLSTARS:",dest)
