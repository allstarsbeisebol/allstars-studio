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
name=ep.get("athlete","").strip()
if not name:raise SystemExit("Atleta não informado")
references=[]
for source in registry["sources"]:
    query="site:"+source["domain"]+" "+name+" baseball"
    references.append({"name":source["name"],"homepage":source["url"],"search_url":"https://www.google.com/search?q="+quote_plus(query),"focus":source["focus"],"status":"LINK DE PESQUISA — NÃO VERIFICADO"})
report={"athlete":name,"episode_id":ep.get("id"),"research_sites":references,
        "episode_source_urls":[{"url":u,"status":"FORNECIDA NO RASCUNHO — VERIFICAÇÃO HUMANA NECESSÁRIA"} for u in ep.get("sources",[])],
        "verified_claims":[],"verification_status":"PENDENTE",
        "notice":"Não há acesso automático verificado às páginas nem validação das alegações históricas. Não apresentar os links de busca como fontes já consultadas."}
out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("Pesquisa orientada para",name,":",len(references),"sites cadastrados")
