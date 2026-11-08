#!/usr/bin/env python3
"""Pacote de pesquisa editorial reproduzível; sem scraping ou afirmações inventadas.

Os endereços de busca são trilhas de pesquisa, não links de comprovação.
Fontes específicas do episódio são preservadas sem serem marcadas como verificadas.
"""
import argparse, json
from pathlib import Path
from urllib.parse import quote_plus
P=argparse.ArgumentParser()
P.add_argument("--episode",default="data/episode.json")
P.add_argument("--output",default="output/pesquisa.json")
args=P.parse_args()
root=Path(__file__).resolve().parents[1]
ep=json.loads(Path(args.episode).read_text(encoding="utf-8"))
registry=json.loads((root/"data/research_sources.json").read_text(encoding="utf-8"))
name=str(ep.get("subject") or ep.get("athlete") or "").strip()
if not name:raise SystemExit("Assunto não informado")
references=[]
for source in registry["sources"]:
    query="site:"+source["domain"]+" "+name+" baseball"
    references.append({"name":source["name"],"homepage":source["url"],"search_url":"https://www.google.com/search?q="+quote_plus(query),"focus":source["focus"],"status":"LINK DE PESQUISA — NÃO VERIFICADO"})
report={"athlete":ep.get("athlete"),"subject":name,"content_type":ep.get("content_type","atleta"),"episode_id":ep.get("id"),"research_sites":references,
        "episode_source_urls":[{"url":u,"status":"FORNECIDA NO RASCUNHO — VERIFICAÇÃO HUMANA NECESSÁRIA"} for u in ep.get("sources",[])],
        "verified_claims":[],"verification_status":"PENDENTE",
        "notice":"Links de busca não foram consultados automaticamente. Um link fornecido pode ter seu HTML lido para criar o rascunho, mas seus fatos não são verificados de forma independente."}
if isinstance(ep.get("editorial_checks"),dict):
    report["editorial_checks"]=ep["editorial_checks"]
if isinstance(ep.get("source_metadata"),dict):
    report["reference_article"]={
        "retrieval":"HTML público lido para elaboração do rascunho",
        **ep["source_metadata"],
        "supporting_paragraph_ids":ep.get("evidence_paragraphs",[]),
        "evidence_note":"Identificadores apenas para auditoria do artigo, não constituem prova externa nem verificação histórica.",
        "rights":"A leitura da página não autoriza reutilizar fotos, ilustrações ou conteúdo integral."
    }
media_file=root/"output/midia.json"
if media_file.is_file():
    try:
        media=json.loads(media_file.read_text(encoding="utf-8"))
        if media.get("status")=="approved_anime":
            report["media"]={
                "status":"Arte anime original aprovada pelo responsável do projeto",
                "visual_mode":"approved_anime",
                "source_note":media.get("source_note"),
                "rights_basis":media.get("rights_basis"),
                "source_repo_file":media.get("source_repo_file"),
                "note":"A representação é ilustrativa; não é fotografia nem documento histórico."
            }
        elif media.get("status") in ("existing","downloaded"):
            record=media.get("record",{})
            report["media"]={
                "source":"Wikimedia Commons","url":record.get("source_url"),
                "author":record.get("author"),"license":record.get("license"),
                "license_url":record.get("license_url"),
                "status":"Licença e autoria informadas pelo Commons; confirmar antes da publicação",
                "note":"Foto não prova a narrativa histórica do roteiro."
            }
        else:
            report["media"]={"status":"Nenhuma foto licenciada encontrada; cartoon original utilizado","visual_mode":"original_cartoon","attribution":"ALLSTARS Studio","representation":"Personagem fictício ilustrativo; não retrato histórico fiel do atleta"}
    except (ValueError,OSError):
        report["media"]={"status":"Dados da imagem indisponíveis"}
out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("Pesquisa orientada para",name,":",len(references),"sites cadastrados")
