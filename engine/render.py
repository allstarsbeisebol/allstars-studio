#!/usr/bin/env python3
"""Reel ALLSTARS cinematográfico: cenas editoriais, zoom/pan, fades e legendas.

Não inventa fotografia nem retoca a marca; reutiliza o compositor da capa.
"""
import argparse,json,subprocess
from pathlib import Path
from PIL import Image
from poster import poster

p=argparse.ArgumentParser()
p.add_argument("--episode",default="data/episode.json")
p.add_argument("--audio",default="output/narracao.wav")
p.add_argument("--out-dir",default="output")
args=p.parse_args()
ep=json.loads(Path(args.episode).read_text(encoding="utf-8"))
out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
audio=Path(args.audio)
if not audio.exists():raise SystemExit("Narração não encontrada: "+str(audio))
proc=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(audio)],capture_output=True,text=True,check=True)
duration=float(proc.stdout.strip())
if duration<=1:raise SystemExit("Áudio inválido ou muito curto")
screens=[str(x).strip() for x in ep.get("screens",[]) if str(x).strip()]
scenes=[ep.get("title","ALÉM DO JOGO")]+screens[:5]
if len(scenes)==1:scenes.append(ep.get("athlete","HISTÓRIAS REAIS"))
photos=[]
for i,message in enumerate(scenes):
    path=out/f"cena_{i:02d}.jpg"
    if i==0 and (out/"capa.png").is_file():
        with Image.open(out/"capa.png") as im:im.convert("RGB").save(path,quality=91,subsampling=0)
    else:
        poster(ep,headline=message,index=i,total=len(scenes)-1).save(path,quality=91,subsampling=0)
    photos.append(path)
# Uso editorial: abertura mais curta, cenas centrais dividindo o tempo total.
if len(scenes)>1 and duration>8:
    opener=min(3.3,duration*.16)
    timings=[opener]+[(duration-opener)/(len(scenes)-1)]*(len(scenes)-1)
else:timings=[duration/len(scenes)]*len(scenes)

# Se as legendas ainda não foram montadas, gerar alternativa estimada.
ass=out/"legendas.ass"
if not ass.is_file():
    subprocess.run(["python","engine/subtitles.py","--episode",args.episode,"--audio",str(audio),"--out-dir",str(out)],check=True)

fade=.48
inputs=[]
for path,seg in zip(photos,timings):
    inputs+=["-loop","1","-framerate","24","-t",f"{seg+fade:.3f}","-i",str(path)]
inputs+=["-i",str(audio)]
filters=[]
for i in range(len(photos)):
    # Ken Burns em intensidade suave, sem deformar o logo.
    filters.append(f"[{i}:v]fps=24,scale=1140:2027:flags=lanczos,"
                   f"crop=1080:1920:x='30+14*sin(t/3+{i})':y='53+14*cos(t/3+{i})',"
                   f"setsar=1,format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[v{i}]")
label="v0";elapsed=0.0
for i in range(1,len(photos)):
    elapsed+=timings[i-1]
    target=f"mix{i}"
    filters.append(f"[{label}][v{i}]xfade=transition=fade:duration={fade}:offset={elapsed:.3f}[{target}]")
    label=target
filters.append(f"[{label}]subtitles=filename='{ass.as_posix()}',format=yuv420p[final]")
output=out/"allstars_reel.mp4"
cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",*inputs,
     "-filter_complex",";".join(filters),"-map","[final]","-map",f"{len(photos)}:a:0",
     "-c:v","libx264","-preset","veryfast","-crf","24","-r","24",
     "-c:a","aac","-b:a","160k","-movflags","+faststart","-t",f"{duration:.3f}",str(output)]
try:
    subprocess.run(cmd,check=True,timeout=1800)
    motion="pan + fades"
except (subprocess.CalledProcessError,subprocess.TimeoutExpired):
    # Renderização segura para máquinas sem filtro xfade; nunca perder o episódio.
    concat=out/"fallback.ffconcat"
    with concat.open("w",encoding="utf-8") as f:
        f.write("ffconcat version 1.0\n")
        for path,seconds in zip(photos,timings):
            f.write("file '"+path.resolve().as_posix()+"'\n")
            f.write(f"duration {seconds:.4f}\n")
        f.write("file '"+photos[-1].resolve().as_posix()+"'\n")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-safe","0","-f","concat","-i",str(concat),"-i",str(audio),
        "-vf",f"fps=24,subtitles=filename='{ass.as_posix()}',format=yuv420p",
        "-c:v","libx264","-preset","veryfast","-crf","24","-c:a","aac","-b:a","160k",
        "-movflags","+faststart","-t",f"{duration:.3f}",str(output)],check=True)
    motion="fallback sem transições"
for field,name in [("caption","legenda_instagram.txt"),("narration","roteiro.txt")]:
    (out/name).write_text(str(ep.get(field,"")),encoding="utf-8")
(out/"fontes.txt").write_text("\n".join(ep.get("sources",[])),encoding="utf-8")
print("Reel pronto:",output,"| segundos:",round(duration,1),"| movimento:",motion)
