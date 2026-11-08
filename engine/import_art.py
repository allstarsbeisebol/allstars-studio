#!/usr/bin/env python3
"""Normaliza uma imagem enviada para capa 9:16 e versão 3:4.

Não gera conteúdo nem depende de serviço de imagem pago. Não mistura a
imagem de outros pedidos e nunca altera o arquivo original no GitHub Release.
"""
import argparse,json,re
from pathlib import Path
from PIL import Image,ImageFilter,ImageOps,ImageDraw

Image.MAX_IMAGE_PIXELS=24_000_000
W,H=1080,1920
BACKGROUND=(7,22,50)

def render_import(image_file,episode,output):
    path=Path(image_file)
    expected=str(episode.get("art_image_asset") or "")
    if not re.fullmatch(r"external-r[1-9]\d{0,4}-[a-f0-9]{12}\.jpg",expected):
        raise ValueError("Imagem aprovada inválida no roteiro.")
    if path.name!=expected:
        raise ValueError("O arquivo enviado não pertence à versão atual da capa.")
    if not path.is_file() or path.stat().st_size>1_900_000:
        raise ValueError("Imagem externa ausente ou muito grande.")
    with Image.open(path) as image:
        if image.format!="JPEG":
            raise ValueError("Somente imagem JPEG normalizada é aceita nesta etapa.")
        if min(image.size)<256 or image.width*image.height>24_000_000:
            raise ValueError("Imagem externa com resolução inadequada.")
        art=ImageOps.exif_transpose(image).convert("RGB")
    mode=str(episode.get("art_image_fit") or "contain")
    if mode=="cover":
        canvas=ImageOps.fit(art,(W,H),method=Image.Resampling.LANCZOS,centering=(.5,.46))
    elif mode in ("blur","contain"):
        if mode=="blur":
            bg=ImageOps.fit(art,(W,H),method=Image.Resampling.LANCZOS)
            bg=bg.filter(ImageFilter.GaussianBlur(65))
            bg=Image.blend(bg,Image.new("RGB",(W,H),BACKGROUND),.40)
        else:
            bg=Image.new("RGB",(W,H),BACKGROUND)
        foreground=ImageOps.contain(art,(W,H),method=Image.Resampling.LANCZOS)
        bg.paste(foreground,((W-foreground.width)//2,(H-foreground.height)//2))
        canvas=bg
    else:raise ValueError("Tipo de enquadramento não permitido.")
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(dest,format="PNG",optimize=True)
    # O perfil do Instagram mostra a região central 1080x1440.
    profile=canvas.crop((0,240,W,1680))
    profile.save(dest.parent/"capa_perfil_3x4.png",format="PNG",optimize=True)
    return {"source":"user_supplied_image","fit":mode,"dimensions":[W,H],
            "source_filename":expected,"rights_confirmed":True,
            "note":"Arte enviada pelo editor. A autoria, veracidade e os direitos da imagem devem ser conferidos antes de publicar."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",default="output/selected.json")
    p.add_argument("--image",required=True)
    p.add_argument("--output",default="output/capa.png")
    args=p.parse_args()
    ep=json.loads(Path(args.episode).read_text(encoding="utf-8"))
    meta=render_import(args.image,ep,args.output)
    print("Capa externa importada:",json.dumps(meta,ensure_ascii=False))

if __name__=="__main__":main()
