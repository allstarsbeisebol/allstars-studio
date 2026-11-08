#!/usr/bin/env python3
"""Prepara logo oficial da própria página ALLSTARS, sem desenhar logo com IA.

Fonte da marca é o site oficial ALLSTARS (repositório allstarsbeisebol/site).
A versão 180x97 do repositório é apenas contingência; preferimos original maior.
O PNG selecionado fica anexado ao release do pedido e reaproveitado no MP4.
"""
import base64,io,urllib.request
from pathlib import Path
from PIL import Image,ImageFilter

ROOT=Path(__file__).resolve().parents[1]
BRAND_SOURCE="https://i.imgur.com/iGbHnOr.png"
TARGET=ROOT/"output/logo-oficial.png"
MAX_BYTES=4_000_000

def parse_logo(raw):
    if len(raw)>MAX_BYTES:raise ValueError("Imagem da marca grande demais.")
    with Image.open(io.BytesIO(raw)) as src:
        if src.format!="PNG":raise ValueError("O logotipo oficial precisa ser PNG.")
        image=src.convert("RGBA")
    if image.width<500 or image.height<250:
        raise ValueError("O logotipo remoto não tem resolução suficiente para a capa.")
    ratio=image.width/max(1,image.height)
    if ratio<1.15 or ratio>4.5 or image.width*image.height>22_000_000:
        raise ValueError("Formato da logo incompatível.")
    return image

def prepare(destination=TARGET,opener=urllib.request.urlopen):
    dest=Path(destination)
    dest.parent.mkdir(parents=True,exist_ok=True)
    try:
        req=urllib.request.Request(BRAND_SOURCE,headers={
            "User-Agent":"ALLSTARS-Studio/1.0 (official-brand-reference)",
            "Accept":"image/png"
        })
        with opener(req,timeout=8) as response:
            if str(response.headers.get("Content-Type","")).split(";")[0].strip().lower()!="image/png":
                raise ValueError("Resposta não é PNG.")
            payload=response.read(MAX_BYTES+1)
        logo=parse_logo(payload)
        source="official_site_hd"
    except (OSError,ValueError,TimeoutError,urllib.error.URLError) as err:
        # Em operação offline não inventar marca; recuperar arquivo original.
        fallback=ROOT/"brand/logo.b64"
        logo=Image.open(io.BytesIO(base64.b64decode(fallback.read_text(encoding="ascii").strip()))).convert("RGBA")
        source="repo_fallback_180px"
        print("AVISO: logo HD indisponível; usando marca original reduzida.",type(err).__name__)
    logo.save(dest,format="PNG",optimize=True)
    print("Logo ALLSTARS:",source,logo.width,"x",logo.height)
    return {"source":source,"width":logo.width,"height":logo.height}

if __name__=="__main__":prepare()
