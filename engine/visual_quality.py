#!/usr/bin/env python3
"""Classifica a origem visual do episódio e protege o padrão aprovado."""
import argparse,json
from pathlib import Path
from anime_assets import find_approved_anime
from poster import licensed_photo

p=argparse.ArgumentParser()
p.add_argument("--episode",default="output/selected.json")
p.add_argument("--output",default="output/qualidade_visual.json")
args=p.parse_args()

ep=json.loads(Path(args.episode).read_text(encoding="utf-8"))
approved=find_approved_anime(ep) if ep.get("content_type","atleta")=="atleta" else None
if approved is not None:
    info=approved[1]
    data={
      "mode":"anime_aprovado",
      "premium":True,
      "message":"Arte anime premium aprovada especificamente para este atleta.",
      "source":info.get("source_note","Arte original aprovada"),
      "rights_basis":info.get("rights_basis")
    }
elif ep.get("content_type","atleta")=="atleta" and licensed_photo(ep) is not None:
    data={
      "mode":"foto_licenciada",
      "premium":True,
      "message":"Fotografia real cadastrada com metadados de licença. Revisar direitos antes da publicação."
    }
else:
    thematic=ep.get("content_type","atleta")!="atleta"
    data={
      "mode":"composicao_tematica" if thematic else "cartoon_contingencia",
      "premium":False,
      "message":("Composição temática original com elementos de beisebol; revisar adequação visual e direitos antes da publicação." if thematic else "A capa utiliza o desenho de contingência; ainda NÃO corresponde ao novo padrão de anime premium aprovado. Revise a imagem antes de publicar."),
      "notice":("Conteúdo coletivo utiliza elementos temáticos, não retrato de atleta." if thematic else "Sem foto licenciada e sem arte anime previamente aprovada para este atleta.")
    }

out=Path(args.output)
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print("Qualidade visual:",data["mode"],"| premium:",data["premium"])
