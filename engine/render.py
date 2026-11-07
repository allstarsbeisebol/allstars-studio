#!/usr/bin/env python3
"""Reel 1080x1920 com fundos gráficos originais e áudio narrado. Sem usar fotos protegidas."""
import argparse, json, math, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

p=argparse.ArgumentParser()
p.add_argument("--episode",default="data/episode.json")
p.add_argument("--audio",default="output/narracao.wav")
p.add_argument("--out-dir",default="output")
args=p.parse_args()
ep=json.loads(Path(args.episode).read_text(encoding="utf-8"))
out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
audio=Path(args.audio)
if not audio.is_file():raise SystemExit("Áudio não encontrado: "+str(audio))
def media_duration(path):
    res=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
      "-of","default=noprint_wrappers=1:nokey=1",str(path)],capture_output=True,text=True,check=True)
    return float(res.stdout.strip())
duration=media_duration(audio)
font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(n):return ImageFont.truetype(font_path,n)
def wrap(draw,text,font,width):
    lines=[];current=""
    for word in text.split():
        guess=(current+" "+word).strip()
        if draw.textbbox((0,0),guess,font=font)[2] > width and current:
            lines.append(current);current=word
        else:current=guess
    if current:lines.append(current)
    return lines
scenes=[ep.get("title","ALÉM DO JOGO")]+ep.get("screens",[])[:5]
scenes=scenes or ["ALÉM DO JOGO"]
time_per=duration/len(scenes)
concat=[]
for i,message in enumerate(scenes):
    im=Image.new("RGB",(1080,1920));pix=im.load()
    for y in range(1920):
        t=y/1919
        for x in range(1080):
            stripe=0.10*math.sin(x/160+y/220)
            r=int(max(0,min(255,9+37*t+12*stripe)))
            g=int(max(0,min(255,26+29*(1-t))))
            b=int(max(0,min(255,65+106*(1-t)+25*stripe)))
            pix[x,y]=(r,g,b)
    d=ImageDraw.Draw(im,"RGBA")
    d.ellipse((560,250,1550,1250),outline=(230,190,90,130),width=6)
    d.ellipse((605,300,1470,1170),outline=(230,190,90,90),width=2)
    d.rectangle((0,1440,1080,1920),fill=(5,13,35,175))
    d.rectangle((68,220,82,410),fill=(228,60,62,255))
    d.text((98,125),"ALLSTARS  BEISEBOL",font=f(57),fill=(255,255,255,255))
    d.text((98,208),"ALÉM DO JOGO  /  HISTÓRIAS REAIS",font=f(29),fill=(242,192,98,255))
    font=f(69 if i==0 else 75)
    lines=wrap(d,str(message).upper(),font,884)
    start_y=790-max(0,(len(lines)-2))*58
    for j,line in enumerate(lines):d.text((94,start_y+j*104),line,font=font,fill=(255,255,255,255),stroke_width=1,stroke_fill=(10,18,38,255))
    d.text((94,1560),str(ep.get("athlete","")).upper(),font=f(59),fill=(241,195,96,255))
    d.text((94,1660),f"EPISÓDIO ALLSTARS   •   {i+1:02d}/{len(scenes):02d}",font=f(27),fill=(235,240,255,255))
    fname=out/f"cena_{i:02d}.png";im.save(fname)
    concat.append((fname,time_per))
with (out/"video.ffconcat").open("w",encoding="utf-8") as fd:
    fd.write("ffconcat version 1.0\n")
    for path,seconds in concat:fd.write("file '"+path.resolve().as_posix()+"'\n"+"duration "+str(seconds)+"\n")
    fd.write("file '"+concat[-1][0].resolve().as_posix()+"'\n")
output=out/"allstars_reel.mp4"
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-safe","0","-f","concat","-i",str(out/"video.ffconcat"),
 "-i",str(audio),"-vf","fps=24,format=yuv420p,scale=1080:1920","-c:v","libx264","-preset","veryfast","-crf","26",
 "-c:a","aac","-b:a","160k","-movflags","+faststart","-t",str(duration),str(output)],check=True)
(out/"legenda_instagram.txt").write_text(ep.get("caption",""),encoding="utf-8")
(out/"fontes.txt").write_text("\n".join(ep.get("sources",[])),encoding="utf-8")
(out/"roteiro.txt").write_text(ep.get("narration",""),encoding="utf-8")
print("Vídeo:",output,"Duração:",round(duration,1),"s")
