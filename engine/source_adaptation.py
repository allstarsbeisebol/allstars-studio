"""Adapta referências bloqueadas em um roteiro ALLSTARS pesquisado, sem inventar fatos.

A URL original continua identificada como NÃO LIDA. Fontes complementares
pesquisadas pelo Gemini são registradas separadamente e precisam de revisão.
"""
from __future__ import annotations
import re
import urllib.parse

GENERIC_PATHS={
    "watch","shorts","reel","reels","p","posts","post","status","videos",
    "video","story","stories","photo","photos","share","read","view",
    "article","articles","news","noticias","noticia","page","pages",
    "media","embed","player","index","html","amp","link","links",
}
OPAQUE=re.compile(r"^[a-zA-Z0-9_-]{13,}$")
SPACE=re.compile(r"\s+")

def normalize_words(value):
    return SPACE.sub(" ",str(value or "")).strip()

def describe_reference(req):
    """Use input words or a meaningful URL slug, never opaque social IDs."""
    subject=normalize_words(req.get("subject",""))
    if subject:return subject[:160], "subject"
    pasted=normalize_words(req.get("reference_text",""))
    if len(pasted.split())>=2 and len(pasted)>=10:
        # User words are a search clue, not independently confirmed facts.
        sentence=re.split(r"(?<=[.!?])\s+",pasted,maxsplit=1)[0]
        return sentence[:160], "user_text_hint"
    for url in req.get("urls",[]):
        path=urllib.parse.urlsplit(url).path
        parts=[urllib.parse.unquote(p) for p in path.split("/") if p]
        for part in reversed(parts):
            clean=re.sub(r"\.(?:html?|php|aspx|pdf)$","",part,flags=re.I).strip()
            if not clean or OPAQUE.fullmatch(clean):continue
            terms=[w for w in re.split(r"[-_+.]+",clean) if w and w.casefold() not in GENERIC_PATHS]
            if len(terms)<2 or len(" ".join(terms))<13:continue
            if not all(re.fullmatch(r"[^\W\d_][\wÀ-ÿ]{2,}",w,flags=re.U) for w in terms[:8]):continue
            return " ".join(terms[:18])[:160], "url_slug_hint"
    return "", "insufficient_context"

def adapt_with_research(req,unread):
    """One grounded search; do not silently switch to an unrelated story."""
    topic,origin=describe_reference(req)
    if not topic:
        raise ValueError(
            "Não consegui ler os links e eles não revelam o assunto. "
            "Informe um título/assunto ou cole algumas frases da publicação; "
            "não criarei uma história aleatória."
        )
    from topic_generate import create_topic
    try:
        ep=create_topic({**req,"subject":topic})
    except ValueError as exc:
        raise ValueError(
            "O Studio tentou pesquisar o mesmo assunto em outras fontes, "
            "mas não obteve referências verificáveis: "+str(exc)[:155]
        ) from exc
    grounding=list(ep.get("sources",[]))
    original=list(req.get("urls",[]))
    ep["sources"]=list(dict.fromkeys(original+grounding))
    ep["requested_subject"]=req.get("subject","")
    ep["original_reference_urls"]=original
    ep["source_mode"]="allstars_complementary_research"
    ep["editorial_status"]=(
        "PRÉVIA ALLSTARS — LINKS ORIGINAIS NÃO LIDOS; "
        "ROTEIRO BASEADO EM PESQUISA COMPLEMENTAR — REVISÃO OBRIGATÓRIA"
    )
    ep["editorial_checks"]={
        "status":"PESQUISA COMPLEMENTAR — NÃO CONFIRMA O CONTEÚDO DOS LINKS ORIGINAIS",
        "verified_independently":False,
        "notice":"Fontes complementares fundamentam apenas os fatos que elas próprias sustentam.",
    }
    ep["source_metadata"]={
        **(ep.get("source_metadata") or {}),
        "source_origin":"fallback_to_public_research",
        "subject_hint_origin":origin,
        "submitted_reference_count":len(original),
        "readable_reference_count":0,
        "unread_references":unread,
        "reference_text_supplied":bool(req.get("reference_text")),
        "original_urls_verified":False,
        "complementary_source_urls":grounding,
        "verified_independently":False,
    }
    ep["unique_art_required"]=True
    return ep
