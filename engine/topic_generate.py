#!/usr/bin/env python3
"""Roteiro sob demanda por assunto, usando buscas com fontes rastreáveis."""
import datetime,json,os,re,socket,sys,urllib.error,urllib.request
from pathlib import Path
from content_request import parse
from from_link import ROOT, validate

def create_topic(request):
    kind=request["content_type"]
    subject=request["subject"].strip()
    if not subject:raise ValueError("Informe um assunto para gerar sem link.")
    key=os.getenv("GEMINI_API_KEY","").strip()
    if not key:raise ValueError("Configure GEMINI_API_KEY para gerar por assunto com pesquisa.")
    model=os.getenv("GEMINI_MODEL","gemini-3.5-flash-lite")
    if not re.fullmatch(r"[A-Za-z0-9._-]+",model):raise ValueError("Modelo Gemini inválido.")
    guides={
        "atleta":"biografia documentada de um atleta",
        "tema":"panorama de 3 a 4 pontos sobre o tema",
        "noticia":"notícia datada com contexto e impacto; não declarar notícias antigas como atuais",
        "lista":"lista baseada em critérios claros; jamais inventar posições",
        "explicativo":"explicação objetiva com exemplos verificáveis",
        "auto":"formato apropriado para o assunto"
    }
    prompt=(
       "Você produz roteiros editoriais em português brasileiro para ALLSTARS Beisebol. "
       "Use busca na internet. Não invente fatos, anos, estatísticas, jogadores ou referências. "
       "Assunto: "+subject+". Formato: "+guides[kind]+". "
       "Produza narração de 105 a 145 palavras, quatro telas curtas e legenda com pergunta. "
       "Responda apenas JSON: athlete (nome se indivíduo, senão string vazia), subject, "
       "title, narration, screens (lista de quatro), caption. "
       "Rankings exigem critério sustentado. Se não houver fontes, não gere conteúdo."
    )
    payload=json.dumps({
       "contents":[{"parts":[{"text":prompt}]}],
       "tools":[{"google_search":{}}],
       "generationConfig":{"temperature":0.2}
    }).encode("utf-8")
    api="https://generativelanguage.googleapis.com/v1beta/models/"+model+":generateContent"
    req=urllib.request.Request(api,data=payload,headers={
       "Content-Type":"application/json","x-goog-api-key":key
    },method="POST")
    try:
        with urllib.request.urlopen(req,timeout=55) as response:
            result=json.load(response)
    except urllib.error.HTTPError as error:
        diagnoses={400:"modelo ou busca incompatíveis com esta chave",401:"chave inválida",403:"sem permissão",404:"modelo não disponível",429:"cota gratuita esgotada",503:"serviço indisponível"}
        raise ValueError("Pesquisa Gemini HTTP "+str(error.code)+": "+diagnoses.get(error.code,"falha do serviço")+".") from None
    except (TimeoutError,socket.timeout,urllib.error.URLError):
        raise ValueError("A pesquisa Gemini demorou para responder; tente novamente.") from None
    candidates=result.get("candidates") or []
    if not candidates:raise ValueError("A IA não retornou conteúdo pesquisado.")
    candidate=candidates[0]
    grounding=candidate.get("groundingMetadata") or {}
    chunks=grounding.get("groundingChunks") or []
    urls=[]
    for chunk in chunks:
        raw=(chunk.get("web") or {}).get("uri")
        if not isinstance(raw,str):continue
        try:normalized=validate(raw)
        except (ValueError,TypeError):continue
        if normalized not in urls:urls.append(normalized)
    if not urls:raise ValueError("A busca não retornou URLs públicas rastreáveis. Nenhum episódio foi criado sem fontes.")
    raw="".join(str(part.get("text","")) for part in (candidate.get("content",{}).get("parts") or [])).strip()
    raw=re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$","",raw)
    try:out=json.loads(raw)
    except (ValueError,TypeError):raise ValueError("A pesquisa não retornou um roteiro JSON válido.") from None
    for field in ("title","narration","caption"):
        if not isinstance(out.get(field),str) or not out[field].strip():raise ValueError("Roteiro incompleto: "+field)
    if not isinstance(out.get("screens"),list) or len(out["screens"])<3:raise ValueError("A IA não forneceu telas suficientes.")
    if not 80<=len(out["narration"].split())<=170:raise ValueError("Narração fora do tamanho esperado.")
    out["screens"]=[str(value)[:95] for value in out["screens"][:4]]
    generated_athlete=str(out.get("athlete") or "").strip()
    out["subject"]=subject
    out["athlete"]=(generated_athlete or subject)[:160]
    out["content_type"]=kind if kind!="auto" else ("atleta" if generated_athlete else "tema")
    out["sources"]=urls[:12]
    out["id"]=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-topic"
    out["approved"]=False
    out["media_approved"]=False
    out["source_mode"]="topic_research"
    out["editorial_status"]="RASCUNHO COM PESQUISA AUTOMÁTICA — fatos e fontes não verificados independentemente"
    out["source_metadata"]={"research_method":"Gemini Google Search grounding","returned_source_count":len(urls),"verified_independently":False}
    return out

def main():
    event=json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    request=parse((event.get("issue") or {}).get("body") or "")
    episode=create_topic(request)
    output=ROOT/"output";output.mkdir(parents=True,exist_ok=True)
    (output/"selected.json").write_text(json.dumps(episode,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Assunto pesquisado:",episode["subject"],"| fontes retornadas:",len(episode["sources"]))
if __name__=="__main__":
    try:main()
    except (ValueError,OSError) as error:
        output=ROOT/"output";output.mkdir(parents=True,exist_ok=True)
        msg=str(error).replace("\r"," ").replace("\n"," ")[:360]
        (output/"production_failure.txt").write_text(msg,encoding="utf-8")
        print("ERRO EDITORIAL:",msg,file=sys.stderr)
        sys.exit(1)
