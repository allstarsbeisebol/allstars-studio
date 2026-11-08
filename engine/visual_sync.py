#!/usr/bin/env python3
"""Arquiva capas ALLSTARS no Supabase e consulta a memória editorial.

Não modifica produção de áudio/vídeo. Usa apenas bibliotecas Python existentes.
Sem credenciais de servidor, preserva o GitHub Releases como destino original.
"""
from __future__ import annotations
import argparse,hashlib,io,json,os,urllib.error,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path

PROJECT="alrgqmwnynybawenyugb"
URL="https://"+PROJECT+".supabase.co"
BUCKET="allstars-visual"

def enabled():
    return os.getenv("SUPABASE_URL","").rstrip("/")==URL and bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

def api(path,body=None,method=None,headers=None):
    if not enabled():raise ValueError("Supabase não configurado ou projeto incorreto.")
    key=os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    data=(body if isinstance(body,bytes) else json.dumps(body,ensure_ascii=False).encode()) if body is not None else None
    req=urllib.request.Request(URL+path,data=data,method=method or ("POST" if body is not None else "GET"),
        headers={"apikey":key,"Authorization":"Bearer "+key,
                 **({"Content-Type":"application/json"} if isinstance(body,(dict,list)) else {}),
                 **(headers or {})})
    try:
        with urllib.request.urlopen(req,timeout=12) as response:
            raw=response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        # Nunca registrar credenciais no log.
        if exc.code==409:return {"conflict":True}
        raise RuntimeError("Supabase não aceitou a sincronização (HTTP "+str(exc.code)+")") from None

def rest(table,query="",body=None,method=None,prefer=None):
    path="/rest/v1/"+table+("?"+query if query else "")
    return api(path,body,method,{"Prefer":prefer} if prefer else {})

def issue_id(ep):
    n=ep.get("episode_number")
    return int(n) if str(n).isdigit() and 0<int(n)<1_000_000_000 else None

def memory(output="output/style_memory.json"):
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    data=[]
    if enabled():
        data=rest("allstars_style_memory",
              "select=preference,summary,subject_tags,confidence&active=eq.true&curator_approved=eq.true&order=confidence.desc&limit=10") or []
    safe=[{"preference":row["preference"],
           "summary":" ".join(str(row.get("summary","")).split())[:240]}
          for row in data if row.get("preference") in ("prefer","avoid") and row.get("summary")]
    dest.write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Memória editorial ativa:",len(safe))
    return safe

def cover_bytes(path):
    from PIL import Image,ImageOps
    with Image.open(path) as original:
        img=ImageOps.exif_transpose(original).convert("RGB")
    if min(img.size)<256:raise ValueError("Capa pequena demais para arquivar.")
    img.thumbnail((1080,1920),Image.Resampling.LANCZOS)
    for quality in (87,78,67):
        buffer=io.BytesIO()
        img.save(buffer,format="JPEG",quality=quality,optimize=True)
        raw=buffer.getvalue()
        if len(raw)<1_900_000:return raw,img.width,img.height
    raise ValueError("Não foi possível otimizar a capa sem ultrapassar o limite.")

def single(items):
    if not isinstance(items,list) or not items or not items[0].get("id"):
        raise ValueError("Supabase não retornou o registro esperado.")
    return items[0]

def archive(ep,stage,root=Path("output")):
    if not enabled():
        print("SUPABASE VISUAL: ignorado — configure SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY como secrets do GitHub Actions.")
        return {"status":"skipped_not_configured"}
    issue=issue_id(ep)
    if issue is None:
        print("SUPABASE VISUAL: episódio sem número de pedido, ignorado.")
        return {"status":"skipped_no_issue"}
    if stage not in ("preview","published"):raise ValueError("Etapa de armazenamento inválida.")
    revision=int(ep.get("art_revision") or 1)
    if revision<1 or revision>99999:raise ValueError("Versão inválida.")
    title=str(ep.get("title") or ep.get("subject") or "Episódio ALLSTARS")[:160]
    subject=str(ep.get("subject") or "")[:160]
    current="published" if stage=="published" else "art_review"
    row=single(rest("allstars_episodes","on_conflict=github_issue_number",
        [{"github_issue_number":issue,"title":title,"subject":subject,"editorial_status":current}],
        prefer="resolution=merge-duplicates,return=representation"))
    external=ep.get("art_source")=="uploaded"
    source="edited_variant" if external else "generated_studio"
    suffix="adapted-upload" if external else "studio"
    path=f"issues/{issue}/r{revision}-{suffix}.jpg"
    rows=rest("allstars_visual_assets","select=id,approval_status&object_path=eq."+urllib.parse.quote(path,safe="")+"&limit=1") or []
    if rows:
        if stage=="published":
            now=datetime.now(timezone.utc).isoformat()
            rest("allstars_visual_assets","id=eq."+rows[0]["id"],
                 {"approval_status":"used_in_video","used_in_video_at":now},method="PATCH")
        return {"status":"already_archived","object_path":path}
    img,w,h=cover_bytes(root/"capa.png")
    upload=api("/storage/v1/object/"+BUCKET+"/"+urllib.parse.quote(path,safe="/"),img,
               headers={"Content-Type":"image/jpeg","x-upsert":"false"})
    if upload and upload.get("conflict"):
        print("A imagem já estava salva no Storage.")
    prompt_file=root/"prompt_imagem_ia.txt"
    if not prompt_file.exists():prompt_file=root/"briefing_arte_anime.txt"
    prompt_id=None
    if prompt_file.is_file():
        pt=prompt_file.read_text(encoding="utf-8")[:12000]
        if pt.strip():
            prompt_id=single(rest("allstars_visual_prompts","",[{
              "episode_id":row["id"],"prompt_type":"external_ai" if external else "initial",
              "provider":"allstars","prompt_text":pt,"revision_number":revision
            }],prefer="return=representation"))["id"]
    now=datetime.now(timezone.utc).isoformat()
    result=single(rest("allstars_visual_assets","", [{
      "episode_id":row["id"],"prompt_id":prompt_id,
      "source_kind":source,"approval_status":"used_in_video" if stage=="published" else "review",
      "bucket_id":BUCKET,"object_path":path,"mime_type":"image/jpeg",
      "file_bytes":len(img),"width_px":w,"height_px":h,
      "sha256_hex":hashlib.sha256(img).hexdigest(),
      "title":title,"rights_basis":"permission" if external else "original_work",
      "rights_confirmed":bool(ep.get("art_rights_confirmed")) if external else True,
      "allow_style_reference":False,
      "used_in_video_at":now if stage=="published" else None,
      "metadata":{"github_issue_number":issue,"revision":revision,
                  "origin":"github_actions","stage":stage,
                  "base_source":"uploaded_original" if external else "generated_studio"}
    }],prefer="return=representation"))
    print("SUPABASE VISUAL:",stage,source,"objeto",path,"tamanho",len(img))
    return {"status":"archived","id":result["id"],"object_path":path}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage",required=True,choices=("memory","preview","published"))
    p.add_argument("--episode",default="output/selected.json")
    p.add_argument("--out",default="output/style_memory.json")
    args=p.parse_args()
    if args.stage=="memory":memory(args.out);return
    ep=json.loads(Path(args.episode).read_text(encoding="utf-8"))
    archive(ep,args.stage)

if __name__=="__main__":main()
