#!/usr/bin/env python3
"""Gera legendas ALLSTARS com texto original e tempos Whisper, quando disponível.

Sem modelo ou sem acesso à rede, usa estimativa proporcional à narração.
As legendas são prévia editorial, não substituem revisão humana.
"""
import argparse, json, re, subprocess, os, math
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("--episode",default="output/selected.json")
p.add_argument("--audio",default="output/narracao.wav")
p.add_argument("--out-dir",default="output")
args=p.parse_args()
episode=json.loads(Path(args.episode).read_text(encoding="utf-8"))
out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)

probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",args.audio],capture_output=True,text=True,check=True)
duration=float(probe.stdout.strip())
words=re.findall(r"\S+",episode.get("narration",""))
if not words:raise SystemExit("Narração vazia para legendagem")

times=[]
method="ESTIMADO"
if os.environ.get("ALLSTARS_WHISPER","0")=="1":
    try:
        from faster_whisper import WhisperModel
        model=WhisperModel("tiny",device="cpu",compute_type="int8",download_root=str(out/"whisper-cache"))
        segments,_=model.transcribe(args.audio,language="pt",beam_size=1,word_timestamps=True,vad_filter=False)
        detected=[w for segment in segments for w in (segment.words or []) if w.start is not None and w.end is not None]
        if .65*len(words)<=len(detected)<=1.45*len(words):
            # Palavras exibidas são as do roteiro original, sem trocar números e nomes pelo ASR.
            for i in range(len(words)):
                j=round(i*(len(detected)-1)/max(1,len(words)-1))
                times.append((max(0,float(detected[j].start)),min(duration,float(detected[j].end))))
            method="WHISPER (tempos aproximados, texto original)"
    except Exception as error:
        print("Whisper indisponível; usando estimativa temporal:",str(error)[:180])

if not times:
    # Ritmo proporcional ao tamanho das palavras, preservando pausas de pontuação.
    weights=[max(2.0,float(len(re.sub(r"\W","",w))))+(2.3 if w.endswith((".",":","!","?")) else 0.0) for w in words]
    total=sum(weights)
    cursor=0.0
    for weight in weights:
        start=duration*cursor/total;cursor+=weight
        times.append((start,duration*cursor/total))

groups=[];i=0
while i<len(words):
    j=min(len(words),i+6)
    # evitar grupos muito rápidos/longos de acordo com a narração
    while j<len(words) and times[j-1][1]-times[i][0]<1.30 and j-i<9:j+=1
    start=max(0,times[i][0]-.06)
    end=min(duration,max(start+.35,times[j-1][1]+.06))
    label=" ".join(words[i:j])
    groups.append((start,end,label))
    i=j

def hhmmss(t,centiseconds=False):
    hours=int(t//3600);minutes=int(t//60)%60;sec=int(t)%60
    if centiseconds:return f"{hours}:{minutes:02}:{sec:02}.{int((t-int(t))*100):02}"
    return f"{hours:02}:{minutes:02}:{sec:02},{int((t-int(t))*1000):03}"

srt=out/"legendas.srt"
with srt.open("w",encoding="utf-8") as f:
    for n,(start,end,label) in enumerate(groups,1):
        f.write(f"{n}\n{hhmmss(start)} --> {hhmmss(end)}\n{label}\n\n")

def escape_ass(s):
    return str(s).replace("{","(").replace("}",")").replace("\\","/").replace("\n"," ")

# ASS: legendas altas o suficiente para não cobrir a marca (área inferior reservada).
header="""[Script Info]
Title: ALLSTARS Beisebol - Alem do Jogo
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ALLSTARS,DejaVu Sans,58,&H00FFFFFF,&H00C0F0F0,&H001A3566,&HD0000010,-1,0,0,0,100,100,0,0,3,5,0,2,60,60,328,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ass=out/"legendas.ass"
with ass.open("w",encoding="utf-8") as f:
    f.write(header)
    for start,end,label in groups:
        f.write(f"Dialogue: 0,{hhmmss(start,True)},{hhmmss(end,True)},ALLSTARS,,0,0,0,,{escape_ass(label)}\n")
(out/"legendas_metadata.json").write_text(json.dumps({"mode":method,"segments":len(groups),"duration_seconds":round(duration,2),"source":"Narração original do episódio","warning":"Revisar sincronização antes de publicar."},ensure_ascii=False,indent=2),encoding="utf-8")
print("Legendas:",ass,"|",srt,"|",len(groups),"trechos | sincronização:",method)
