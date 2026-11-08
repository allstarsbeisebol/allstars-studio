"""Interpreta pedidos do painel ALLSTARS sem executar conteúdo de usuário."""
import re

TYPES={"auto","atleta","tema","noticia","lista","explicativo"}
def parse(body):
    fields={}
    for line in str(body or "").splitlines():
        key,sep,value=line.partition(":")
        if not sep:continue
        key=key.strip().upper()
        if key in ("MODO","TIPO","ASSUNTO","LINK") and key not in fields:
            fields[key]=value.strip()
    kind=fields.get("TIPO","auto").lower()
    if kind not in TYPES:raise ValueError("Tipo de conteúdo inválido.")
    subject=fields.get("ASSUNTO","")
    if len(subject)>160 or any(ord(ch)<32 for ch in subject):
        raise ValueError("Assunto inválido: máximo 160 caracteres.")
    url=fields.get("LINK","")
    if url and not url.startswith("https://"):
        raise ValueError("Utilize um link HTTPS público.")
    mode="link" if url else "auto"
    if kind!="auto" and not subject and not url:
        raise ValueError("Informe o assunto para gerar o episódio.")
    return {"mode":mode,"content_type":kind,"subject":subject,"url":url}

def content_label(req):
    return req.get("subject") or "Histórias do beisebol"
