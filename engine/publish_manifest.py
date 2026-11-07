import os,json,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ep=json.loads((root/"output/selected.json").read_text(encoding="utf-8"))
tag=os.environ["RELEASE_TAG"]
base="https://github.com/liuhelpme/allstars-studio/releases/download/"+tag+"/"
manifest={"available":True,"tag":tag,"updated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"athlete":ep["athlete"],"title":ep["title"],"status":"PRÉVIA EDITORIAL — confira informações históricas, voz e direitos de uso antes de publicar","cover":base+"capa.png","video":base+"allstars_reel.mp4","audio":base+"narracao.mp3","caption":base+"legenda_instagram.txt","script":base+"roteiro.txt","sources":base+"fontes.txt","research":base+"pesquisa.json","release":"https://github.com/liuhelpme/allstars-studio/releases/tag/"+tag}
(root/"latest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
path=root/"data/history.json"
history=json.loads(path.read_text(encoding="utf-8"))
if ep["athlete"] not in history.setdefault("produced",[]):history["produced"].append(ep["athlete"])
path.write_text(json.dumps(history,ensure_ascii=False,indent=2),encoding="utf-8")
