"""Leitura de pedidos do ALLSTARS: URLs múltiplas e texto UTF-8 codificado, sem executar conteúdo."""
import base64,re
TYPES={"auto","atleta","tema","noticia","lista","explicativo"}
def parse(body):
    fields={};urls=[]
    for line in str(body or "").splitlines():
        key,sep,value=line.partition(":")
        if not sep:continue
        key=key.strip().upper()
        if key=="LINK":urls.append(value.strip())
        elif key in ("MODO","TIPO","ASSUNTO","TEXTO_BASE64") and key not in fields:fields[key]=value.strip()
    kind=fields.get("TIPO","auto").lower()
    if kind not in TYPES:raise ValueError("Tipo de conteúdo inválido.")
    subject=fields.get("ASSUNTO","")
    if len(subject)>160 or any(ord(ch)<32 for ch in subject):raise ValueError("Assunto inválido: máximo 160 caracteres.")
    if len(urls)>5 or any(not u.startswith("https://") or len(u)>1900 for u in urls) or len(set(urls))!=len(urls):
        raise ValueError("Informe até 5 links HTTPS públicos diferentes.")
    encoded=fields.get("TEXTO_BASE64","")
    try:
        text=base64.b64decode(encoded,validate=True).decode("utf-8") if encoded else ""
    except (ValueError,UnicodeDecodeError) as ex:raise ValueError("Texto de referência inválido.") from ex
    if len(text)>8000:raise ValueError("Texto de referência excede 8.000 caracteres.")
    if kind!="auto" and not subject and not urls and not text:raise ValueError("Informe o assunto ou as referências para gerar o vídeo.")
    return {"mode":"link" if urls or text else "auto","content_type":kind,"subject":subject,
            "url":urls[0] if urls else "","urls":urls,"reference_text":text}

def content_label(req):
    return req.get("subject") or "Histórias do beisebol"
