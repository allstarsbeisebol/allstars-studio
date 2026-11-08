#!/usr/bin/env python3
"""Imagem externa é ARTE-BASE, nunca um pôster final pronto da outra IA.

O Studio faz enquadramento, contraste, títulos, marca oficial e recorte 3:4
EXATAMENTE como faz com a arte automática. Só a ilustração vem do editor.
"""
import argparse,json,re
from pathlib import Path
from PIL import Image
from poster import poster,profile_from_cover

Image.MAX_IMAGE_PIXELS=24_000_000

def render_import(image_file,episode,output):
    path=Path(image_file)
    expected=str(episode.get("art_image_asset") or "")
    if not re.fullmatch(r"external-r[1-9]\d{0,4}-[a-f0-9]{12}\.jpg",expected):
        raise ValueError("Imagem aprovada inválida no roteiro.")
    if path.name!=expected:
        raise ValueError("O arquivo enviado não pertence à versão atual da capa.")
    if not path.is_file() or path.stat().st_size>1_900_000:
        raise ValueError("Imagem externa ausente ou muito grande.")
    with Image.open(path) as source:
        if source.format!="JPEG":raise ValueError("A imagem externa precisa ser JPEG.")
        if min(source.size)<256 or source.width*source.height>24_000_000:
            raise ValueError("Imagem externa com resolução inadequada.")
    if str(episode.get("art_image_fit") or "contain") not in ("contain","cover","blur"):
        raise ValueError("Tipo de enquadramento não permitido.")
    # A etapa que antes só fazia resize agora gera a MESMA composição
    # editorial da capa automática, com arte externa como plano de fundo.
    canvas=poster(episode,art_override=path)
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(dest,format="PNG",optimize=True)
    profile=profile_from_cover(canvas)
    profile.save(dest.parent/"capa_perfil_3x4.png",format="PNG",optimize=True)
    return {"source":"user_supplied_image",
            "fit":str(episode.get("art_image_fit") or "contain"),
            "dimensions":[1080,1920],
            "profile_dimensions":[1080,1440],
            "layout_applied_by_studio":True,
            "official_logo_used":True,
            "source_filename":expected,
            "rights_confirmed":bool(episode.get("art_rights_confirmed")),
            "note":"A capa final contém imagem do editor como arte-base; layout e marca são aplicados pelo Studio."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode",default="output/selected.json")
    p.add_argument("--image",required=True)
    p.add_argument("--output",default="output/capa.png")
    args=p.parse_args()
    ep=json.loads(Path(args.episode).read_text(encoding="utf-8"))
    meta=render_import(args.image,ep,args.output)
    print("Capa externa com identidade ALLSTARS:",json.dumps(meta,ensure_ascii=False))

if __name__=="__main__":main()
