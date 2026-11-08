#!/usr/bin/env python3
"""Busca opcional de fotografias no Wikimedia Commons, com licença explícita.

Nunca usa arquivos sem metadados suficientes. Não tenta remover marcas d'água,
contornar restrições ou obter imagens em sites com direitos reservados.
A busca pode não encontrar fotos: nesse caso o pôster usa ilustração editorial.
"""
from __future__ import annotations
import argparse, html, json, re, unicodedata, urllib.parse, urllib.request
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageOps

API="https://commons.wikimedia.org/w/api.php"
USER_AGENT="ALLSTARS-Studio-MediaResearch/1.0 (https://github.com/liuhelpme/allstars-studio; editorial single image)"
ALLOWED={"cc0","public domain","pd","cc by 4.0","cc by 3.0","cc by 2.0","cc by 2.5","cc by 1.0"}
MAX_DOWNLOAD=7_500_000

def slug(value):
    s=unicodedata.normalize("NFKD",str(value)).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+","-",s).strip("-")

def plain(value):
    # Wikimedia metadata fields contain limited HTML markup.
    raw=re.sub(r"<[^>]*>"," ",str(value or ""))
    return re.sub(r"\s+"," ",html.unescape(raw)).strip()[:450]

def meta(image,key):
    entry=image.get("extmetadata",{}).get(key,{})
    return plain(entry.get("value","") if isinstance(entry,dict) else "")

def license_allowed(value):
    name=plain(value).lower().replace("creativecommons","cc").strip()
    name=re.sub(r"\s+"," ",name).replace("attribution","by")
    if any(term in name for term in ("noncommercial","non-commercial","-nc","no derivatives","-nd","-sa","sharealike","unfree","fair use")):
        return False
    return name in ALLOWED

def full_name_in(title,athlete):
    cleaned=unicodedata.normalize("NFKD",str(title)).encode("ascii","ignore").decode().casefold()
    cleaned=re.sub(r"[^a-z0-9]+"," ",cleaned)
    name=unicodedata.normalize("NFKD",str(athlete)).encode("ascii","ignore").decode().casefold()
    name=re.sub(r"[^a-z0-9]+"," ",name).strip()
    return bool(name) and name in cleaned

def select_candidate(pages,athlete):
    candidates=[]
    for page in pages.values():
        title=page.get("title","")
        if not full_name_in(title,athlete):continue
        for item in page.get("imageinfo",[])[:1]:
            mime=str(item.get("mime") or "")
            if mime not in ("image/jpeg","image/png"):continue
            if item.get("width",0)<380 or item.get("height",0)<400:continue
            if item.get("size",0)>MAX_DOWNLOAD*2:continue
            license_name=meta(item,"LicenseShortName")
            if not license_allowed(license_name):continue
            url=item.get("thumburl") or item.get("url")
            page_url=item.get("descriptionurl") or ""
            if not url or not page_url:continue
            source=urllib.parse.urlsplit(url)
            if source.scheme!="https" or source.hostname not in ("upload.wikimedia.org","commons.wikimedia.org"):continue
            description=urllib.parse.urlsplit(page_url)
            if description.scheme!="https" or description.hostname!="commons.wikimedia.org":continue
            attribution=meta(item,"Artist") or meta(item,"Attribution")
            if not attribution:continue
            candidates.append({
                "title":title,"url":url,"source_url":page_url,"license":license_name,
                "author":attribution,"license_url":meta(item,"LicenseUrl"),
                "width":item.get("width",0),"height":item.get("height",0),
                "source":"Wikimedia Commons","approved_for_publication":True,
                "license_metadata_checked":True,
                "usage_note":"Metadados de licença do Commons conferidos automaticamente. Antes de publicar, confira titularidade e atribuição."
            })
    candidates.sort(key=lambda c:(c["width"]*c["height"],len(c["title"])),reverse=True)
    return candidates[0] if candidates else None

def opener_get(url,max_bytes):
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json,image/jpeg,image/png"})
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):return None
    with urllib.request.build_opener(NoRedirect).open(req,timeout=15) as response:
        if int(response.headers.get("Content-Length","0"))>max_bytes:
            raise ValueError("Imagem maior que o limite do ALLSTARS.")
        data=response.read(max_bytes+1)
        if len(data)>max_bytes:raise ValueError("Resposta maior que o limite do ALLSTARS.")
        return data

def discover(athlete):
    params={
      "action":"query","format":"json","generator":"search","gsrsearch":f"intitle:\"{athlete}\"",
      "gsrnamespace":"6","gsrlimit":"12","prop":"imageinfo",
      "iiprop":"url|size|mime|extmetadata","iiurlwidth":"1400","maxlag":"5"
    }
    payload=json.loads(opener_get(API+"?"+urllib.parse.urlencode(params),250_000))
    return select_candidate(payload.get("query",{}).get("pages",{}),athlete)

def acquire(episode,repo_root):
    athlete=str(episode.get("athlete","")).strip()
    if len(athlete)<4:return {"status":"skipped","reason":"Atleta não informado."}
    folder=Path(repo_root)/"assets/athletes";folder.mkdir(parents=True,exist_ok=True)
    jpg=folder/(slug(athlete)+".jpg")
    manifest=folder/(slug(athlete)+".license.json")
    if jpg.exists() and manifest.exists():
        record=json.loads(manifest.read_text(encoding="utf-8"))
        if record.get("approved_for_publication") and record.get("source_url") and record.get("license"):
            return {"status":"existing","photo_path":str(jpg),"record":record}
    candidate=discover(athlete)
    if candidate is None:return {"status":"not_found","reason":"Nenhuma foto com licença permitida e identidade suficientemente clara."}
    raw=opener_get(candidate["url"],MAX_DOWNLOAD)
    with Image.open(BytesIO(raw)) as input_image:
        if input_image.format not in ("JPEG","PNG"):
            raise ValueError("Imagem não é JPEG/PNG.")
        image=ImageOps.exif_transpose(input_image).convert("RGB")
        if image.width<380 or image.height<400:
            raise ValueError("Imagem com resolução insuficiente.")
        image.thumbnail((1800,2400),Image.Resampling.LANCZOS)
        image.save(jpg,"JPEG",quality=92,optimize=True)
    record={k:v for k,v in candidate.items() if k!="url"}
    manifest.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
    return {"status":"downloaded","photo_path":str(jpg),"record":record}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--episode",default="output/selected.json")
    parser.add_argument("--output",default="output/midia.json")
    opts=parser.parse_args()
    path=Path(opts.episode)
    episode=json.loads(path.read_text(encoding="utf-8"))
    root=Path(__file__).resolve().parents[1]
    try:
        result=acquire(episode,root)
    except Exception as error:
        # Uma falha de pesquisa não deve impedir a produção do Reel.
        result={"status":"unavailable","reason":str(error)[:160]}
    dest=Path(opts.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Busca de foto:",result["status"])

if __name__=="__main__":main()
