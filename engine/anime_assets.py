"""Banco de artes anime aprovadas por atleta, sem geração paga automática.

A aprovação visual nunca é herdada de outro atleta. Cada imagem requer
metadados vinculando atleta, origem, autorização e estilo editorial.
"""
from __future__ import annotations
import json,re,unicodedata
from pathlib import Path
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"assets"/"anime"

def slug(name):
    ascii_name=unicodedata.normalize("NFKD",str(name)).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+","-",ascii_name).strip("-")

def find_approved_anime(episode):
    """Return (RGB image, metadata) only for exact name-matching approved work."""
    athlete=str(episode.get("athlete","")).strip()
    identifier=slug(athlete)
    if not identifier:return None
    metadata_file=FOLDER/(identifier+".json")
    if not metadata_file.is_file():return None
    try:
        info=json.loads(metadata_file.read_text(encoding="utf-8"))
        if info.get("approved") is not True:return None
        if slug(info.get("athlete",""))!=identifier:return None
        if info.get("visual_type")!="original_anime_illustration":return None
        if not info.get("rights_basis") or not info.get("source_note"):return None
        filename=info.get("file","")
        if filename not in (identifier+".png",identifier+".jpg",identifier+".webp"):return None
        path=FOLDER/filename
        with Image.open(path) as original:
            original=ImageOps.exif_transpose(original)
            if original.width<480 or original.height<850:return None
            if abs(original.width/original.height - 9/16)>.025:return None
            art=original.convert("RGB")
        return art,info
    except (OSError,ValueError,TypeError,KeyError):
        return None

def cover_from_approved_asset(episode):
    result=find_approved_anime(episode)
    if result is None:return None
    art,info=result
    # This is an already finished 9:16 editorial poster. Do not add a
    # second title or redraw the brand mark in the approved artwork.
    return ImageOps.fit(art,(1080,1920),method=Image.Resampling.LANCZOS,centering=(.5,.5)),info

def hero_from_approved_asset(episode):
    result=find_approved_anime(episode)
    if result is None:return None
    art,info=result
    # Only the upper illustrated player part is used in scene cards. This
    # avoids mixing the first poster's baked headline into later scenes.
    art=ImageOps.fit(art,(1080,1920),method=Image.Resampling.LANCZOS)
    return art.crop((0,115,1080,1250)).convert("RGBA"),info
