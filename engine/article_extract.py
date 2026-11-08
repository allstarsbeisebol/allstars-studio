#!/usr/bin/env python3
"""Extrai conteúdo de uma página HTML pública para o editor ALLSTARS.

Somente transforma HTML já baixado: não acessa rede, não lê scripts ativos,
não burla paywalls e não presume que os fatos estão verificados.
"""
import hashlib
import json
import re
from html.parser import HTMLParser

BLOCKS={"p","h1","h2","h3","h4","li","blockquote"}
SKIP={"nav","footer","header","aside","style","noscript","svg","form","button","select","template"}
BOILERPLATE=("accept cookies","privacy policy","cookie policy","sign up for","subscribe to","javascript is required","all rights reserved","cadastre-se para receber","política de privacidade")
MAX_ARTICLE_CHARACTERS=13500

class _Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]
        self.blocks=[]
        self.current=None
        self.meta={}
        self.title_parts=[]
        self.json_parts=[]
        self.ld_scripts=[]
        self.is_ld=False
    def handle_starttag(self,tag,attrs):
        tag=tag.lower()
        attr=dict(attrs)
        if tag=="meta":
            name=(attr.get("property") or attr.get("name") or "").lower()
            if name in ("og:title","twitter:title","description","article:published_time","author"):
                self.meta[name]=str(attr.get("content") or "")[:450]
        if tag=="script" and attr.get("type","").lower().split(";")[0].strip()=="application/ld+json":
            self.is_ld=True
            self.json_parts=[]
        if tag=="br" and self.current is not None:self.current["parts"].append(" ")
        if tag in BLOCKS and not any(t in SKIP or t=="script" for t in self.stack):
            self._finish()
            self.current={"tag":tag,"parts":[],"article":("article" in self.stack),
                          "main":("main" in self.stack)}
        if tag not in ("area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"):
            self.stack.append(tag)
    def handle_endtag(self,tag):
        tag=tag.lower()
        if self.current is not None and self.current["tag"]==tag:self._finish()
        if tag=="script" and self.is_ld:
            snippet="".join(self.json_parts)
            if len(snippet)<=140000:self.ld_scripts.append(snippet)
            self.is_ld=False;self.json_parts=[]
        if tag in self.stack:
            index=len(self.stack)-1-self.stack[::-1].index(tag)
            self.stack=self.stack[:index]
    def handle_data(self,data):
        if self.is_ld:
            self.json_parts.append(data)
            return
        if "title" in self.stack:self.title_parts.append(data)
        if self.current is not None and not any(tag in SKIP or tag=="script" for tag in self.stack):
            self.current["parts"].append(data)
    def _finish(self):
        if self.current is None:return
        block=self.current
        text=re.sub(r"\s+"," ","".join(block["parts"])).strip()
        if text and len(text)>=18 and not any(text.lower().startswith(x) for x in BOILERPLATE):
            self.blocks.append({"text":text,"article":block["article"],"main":block["main"]})
        self.current=None
    def close(self):
        self._finish()
        super().close()

def _json_articles(records):
    bodies=[]
    def visit(obj,depth=0):
        if depth>=8:return
        if isinstance(obj,list):
            for item in obj[:20]:visit(item,depth+1)
        elif isinstance(obj,dict):
            kind=obj.get("@type",[])
            kinds=[kind] if isinstance(kind,str) else kind if isinstance(kind,list) else []
            if any(str(t).lower().endswith(("article","newsarticle","blogposting","reportage")) for t in kinds):
                body=obj.get("articleBody")
                if isinstance(body,str) and len(body.strip())>=400:
                    bodies.append(body[:MAX_ARTICLE_CHARACTERS])
            for value in obj.values():
                if isinstance(value,(dict,list)):visit(value,depth+1)
    for item in records[:8]:
        try:visit(json.loads(item))
        except (ValueError,TypeError,RecursionError):continue
    return sorted(bodies,key=len,reverse=True)

def extract_article(html,url):
    if not isinstance(html,str) or len(html)>1500000:raise ValueError("HTML ausente ou grande demais.")
    parser=_Reader();parser.feed(html);parser.close()
    title=(parser.meta.get("og:title") or parser.meta.get("twitter:title")
           or " ".join(parser.title_parts)).strip()[:240]
    article=[b["text"] for b in parser.blocks if b["article"]]
    main=[b["text"] for b in parser.blocks if b["main"]]
    all_blocks=[b["text"] for b in parser.blocks]
    json_bodies=_json_articles(parser.ld_scripts)
    method="article" if sum(map(len,article))>=400 else "main" if sum(map(len,main))>=400 else "visible_paragraphs"
    selection={"article":article,"main":main,"visible_paragraphs":all_blocks}[method]
    selected_text="\n\n".join(selection)
    # O JSON-LD editorial às vezes contém o artigo integral em páginas cuja
    # renderização principal é JavaScript. Não aceitar apenas títulos/resumos.
    if len(selected_text)<550 and json_bodies and len(json_bodies[0])>len(selected_text):
        selected_text=json_bodies[0]
        method="schema.org/articleBody"
    paragraphs=[]
    seen=set()
    for part in re.split(r"\n{2,}",selected_text):
        part=re.sub(r"[ \t\r\n]+"," ",part).strip()
        if len(part)<22 or part.lower() in seen:continue
        seen.add(part.lower())
        paragraphs.append(part)
    text="\n\n".join(paragraphs)[:MAX_ARTICLE_CHARACTERS]
    if len(text)<500 or len(text.split())<75:
        raise ValueError("Este site não forneceu texto de artigo suficiente. Experimente um link direto para uma biografia ou matéria pública.")
    if not title:title=re.sub(r"\s+"," ",paragraphs[0])[:175]
    return {
        "url":url,"title":title,"text":text,
        "extraction_method":method,"paragraph_count":len(paragraphs),
        "word_count":len(text.split()),
        "content_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "published_at":parser.meta.get("article:published_time",""),
        "author":parser.meta.get("author",""),
        "verification_status":"TEXTO EXTRAÍDO; FATOS NÃO VERIFICADOS"
    }
