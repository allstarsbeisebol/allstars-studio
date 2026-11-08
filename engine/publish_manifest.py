import os,json,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ep=json.loads((root/"output/selected.json").read_text(encoding="utf-8"))
tag=os.environ["RELEASE_TAG"]
base="https://github.com/allstarsbeisebol/allstars-studio/releases/download/"+tag+"/"
manifest={"available":True,"tag":tag,"updated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"athlete":ep.get("athlete"),"subject":ep.get("subject") or ep.get("athlete"),"content_type":ep.get("content_type","atleta"),"title":ep["title"],"status":"PRÉVIA EDITORIAL — confira informações históricas, voz e direitos de uso antes de publicar","cover":base+"capa.png","profile_cover":base+"capa_perfil_3x4.png","video":base+"allstars_reel.mp4","audio":base+"narracao.mp3","caption":base+"legenda_instagram.txt","script":base+"roteiro.txt","sources":base+"fontes.txt","research":base+"pesquisa.json","subtitles":base+"legendas.srt","subtitle_metadata":base+"legendas_metadata.json","media":base+"midia.json","anime_briefing":base+"briefing_arte_anime.txt","visual_quality":base+"qualidade_visual.json","release":"https://github.com/allstarsbeisebol/allstars-studio/releases/tag/"+tag}
quality_file=root/"output/qualidade_visual.json"
if quality_file.is_file():
    quality=json.loads(quality_file.read_text(encoding="utf-8"))
    manifest["visual_mode"]=quality.get("mode","desconhecido")
    manifest["visual_premium"]=bool(quality.get("premium",False))
    manifest["visual_message"]=quality.get("message","Revisar arte antes de publicar.")
    if not manifest["visual_premium"]:
        manifest["status"]="PRÉVIA EDITORIAL — arte ainda NÃO aprovada no padrão anime premium. Revisar antes de publicar."
(root/"latest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
(root/"public/latest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
path=root/"data/history.json"
history=json.loads(path.read_text(encoding="utf-8"))
if ep.get("content_type","atleta")=="atleta" and ep["athlete"] not in history.setdefault("produced",[]):history["produced"].append(ep["athlete"])
path.write_text(json.dumps(history,ensure_ascii=False,indent=2),encoding="utf-8")
