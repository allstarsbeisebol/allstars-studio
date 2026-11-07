#!/usr/bin/env python3
"""Reels gráficos ALLSTARS baseados na Bíblia Visual 2026, sem alterar logotipos."""
import argparse, json, subprocess, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

parser=argparse.ArgumentParser()
parser.add_argument("--episode",default="data/episode.json")
parser.add_argument("--audio",default="output/narracao.wav")
parser.add_argument("--out-dir",default="output")
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
ep=json.loads(Path(args.episode).read_text(encoding="utf-8"))
brand=json.loads((root/"brand/identity.json").read_text(encoding="utf-8"))
out=Path(args.out_dir)
out.mkdir(parents=True,exist_ok=True)
audio=Path(args.audio)
if not audio.exists():raise SystemExit("Narração não encontrada: "+str(audio))
proc=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(audio)],check=True,capture_output=True,text=True)
duration=float(proc.stdout.strip())
if duration<=1:raise SystemExit("Áudio inválido ou muito curto")
def rgb(s):return tuple(bytes.fromhex(s.lstrip("#")))
colors={name:rgb(val) for name,val in brand["colors"].items()}
royal,navy,red,gold,white=[colors[x] for x in ("royal_blue","navy","red","gold","white")]
def find_font(candidates,size):
    for item in candidates:
        if Path(item).exists():return ImageFont.truetype(item,size)
    return ImageFont.load_default()
# Priorizar a tipografia oficial quando estiver instalada; nunca gerar um logo falso.
title_fonts=["/usr/share/fonts/truetype/barlow/BarlowCondensed-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"]
body_fonts=["/usr/share/fonts/truetype/barlow/Barlow-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
def fit_lines(draw,message,font,max_width):
    lines=[];line=""
    for word in str(message).split():
        candidate=(line+" "+word).strip()
        if draw.textbbox((0,0),candidate,font=font)[2]>max_width and line:
            lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    return lines
scenes=[ep.get("title","ALÉM DO JOGO")]+ep.get("screens",[])[:5]
time_per=duration/len(scenes)
frames=[]
for i,message in enumerate(scenes):
    # Gradiente coerente com Azul Escuro e Azul ALLSTARS, criado de forma eficiente.
    strip=Image.new("RGB",(1,1920))
    pixels=strip.load()
    for y in range(1920):
        fraction=y/1919
        pixels[0,y]=tuple(round(navy[c]*(1-fraction)+royal[c]*fraction*.66) for c in range(3))
    im=strip.resize((1080,1920))
    d=ImageDraw.Draw(im)
    # Acabamento editorial: placas, traços de movimento e elementos do diamante.
    d.polygon([(0,0),(1080,0),(1080,370),(0,590)],fill=navy)
    d.polygon([(0,1450),(1080,1290),(1080,1920),(0,1920)],fill=(11,31,66))
    d.line([(810,350),(1030,580),(810,810),(590,580),(810,350)],fill=gold,width=7)
    d.line([(810,400),(980,580),(810,760),(640,580),(810,400)],fill=royal,width=3)
    d.rectangle((65,350,81,550),fill=red)
    d.rectangle((65,560,280,571),fill=gold)
    d.text((70,93),"ALLSTARS  /  BEISEBOL",font=find_font(body_fonts,42),fill=white)
    d.text((70,168),"ALÉM DO JOGO",font=find_font(title_fonts,73),fill=gold)
    d.text((70,261),"HISTÓRIAS REAIS DO BEISEBOL",font=find_font(body_fonts,26),fill=white)
    header=str(message).upper()
    font_size=78 if i==0 else 86
    for attempt in range(7):
        f=find_font(title_fonts,font_size)
        lines=fit_lines(d,header,f,900)
        if len(lines)<=5:break
        font_size-=7
    y=820-45*max(0,len(lines)-2)
    for line in lines:
        d.text((76,y),line,font=f,fill=white,stroke_width=1,stroke_fill=navy)
        y+=108
    d.text((76,1550),str(ep.get("athlete","")).upper(),font=find_font(title_fonts,66),fill=gold)
    d.rectangle((76,1660,1000,1664),fill=red)
    d.text((76,1700),f"EPISÓDIO ALLSTARS  •  {i+1:02d}/{len(scenes):02d}",font=find_font(body_fonts,30),fill=white)
    d.text((76,1780),"AQUI VOCÊ BRILHA!",font=find_font(body_fonts,32),fill=gold)
    path=out/f"cena_{i:02}.png"
    if i==0 and (out/"capa.png").is_file():
        with Image.open(out/"capa.png") as cover:
            cover.convert("RGB").save(path,optimize=True)
    else:
        im.save(path,optimize=True)
    frames.append(path)
concat=out/"video.ffconcat"
with concat.open("w",encoding="utf-8") as f:
    f.write("ffconcat version 1.0\n")
    for image in frames:
        f.write("file '"+image.resolve().as_posix()+"'\n")
        f.write("duration "+str(time_per)+"\n")
    f.write("file '"+frames[-1].resolve().as_posix()+"'\n")
video=out/"allstars_reel.mp4"
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-safe","0","-f","concat","-i",str(concat),"-i",str(audio),"-vf","fps=24,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","25","-c:a","aac","-b:a","160k","-movflags","+faststart","-t",str(duration),str(video)],check=True)
for key,name in [("caption","legenda_instagram.txt"),("narration","roteiro.txt")]:
    (out/name).write_text(ep.get(key,""),encoding="utf-8")
(out/"fontes.txt").write_text("\n".join(ep.get("sources",[])),encoding="utf-8")
print("Reel:",video,"| Duração:",round(duration,1),"s")
