"""Geometria aprovada para legendas de Reels ALLSTARS (1080x1920).

Fonte entre 42 e 54 px, no máximo duas linhas, com largura real calculada
com Pillow. A caixa de leitura não se aproxima das interfaces do Reels.
"""
from PIL import ImageFont, ImageDraw, Image
import re

WIDTH,HEIGHT=1080,1920
LEFT,RIGHT=162,918
TOP,BOTTOM=930,1150
CENTER=(540,1040)
MAX_TEXT_WIDTH=700
MAX_LINES=2
FONT_SIZE=52

def font_path():
    from pathlib import Path
    for path in (
        "/usr/share/fonts/truetype/barlow/Barlow-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        if Path(path).exists():return path
    raise RuntimeError("Nenhuma fonte compatível disponível.")

def fitting_lines(words):
    """Try 52..42 px and return text with explicit line breaks, or None."""
    canvas=ImageDraw.Draw(Image.new("RGB",(1,1)))
    for size in (52,50,48,46,44,42):
        font=ImageFont.truetype(font_path(),size)
        lines=[];current=""
        for word in words:
            test=(current+" "+word).strip()
            if current and canvas.textbbox((0,0),test,font=font)[2]>MAX_TEXT_WIDTH:
                lines.append(current);current=word
            else:current=test
        if current:lines.append(current)
        if len(lines)<=MAX_LINES and all(canvas.textbbox((0,0),x,font=font)[2]<=MAX_TEXT_WIDTH for x in lines):
            return size,lines
    return None

def partition(words,times,max_duration=3.1):
    """Subtitle blocks constrained by measured width and 2-line limit."""
    groups=[];i=0
    while i<len(words):
        candidate=None
        for j in range(i+1,min(len(words),i+11)+1):
            fitted=fitting_lines(words[i:j])
            if fitted is None:break
            elapsed=times[j-1][1]-times[i][0]
            if elapsed>max_duration and j>i+1:break
            candidate=(j,fitted)
        if candidate is None:
            raise ValueError("Uma palavra da legenda não cabe na largura segura de 756 px.")
        j,(size,lines)=candidate
        start=max(0.0,times[i][0]-.04)
        end=max(start+.28,times[j-1][1]+.04)
        groups.append({"start":start,"end":end,"text":" ".join(words[i:j]),"lines":lines,"font_size":size})
        i=j
    return groups

def escape_ass(text):
    return str(text).replace("\\","/").replace("{","(").replace("}",")").replace("\n"," ")

def ass_dialogues(groups,formatter):
    """Opaque/translucent full-width panel, plus centered explicit line-breaks."""
    lines=[]
    for row in groups:
        start,end=formatter(row["start"]),formatter(row["end"])
        box=(r"{\an7\pos(0,0)\p1\bord0\shad0\1c&H66351A&\1a&H30&}"
             f"m {LEFT} {TOP} l {RIGHT} {TOP} {RIGHT} {BOTTOM} {LEFT} {BOTTOM}"
             r"{\p0}")
        text=r"{\an5\pos(540,1040)\fs"+str(row["font_size"])+r"\bord3\shad0}"+r"\N".join(escape_ass(x) for x in row["lines"])
        lines.append(f"Dialogue: 0,{start},{end},ALLSTARS,,0,0,0,,{box}")
        lines.append(f"Dialogue: 1,{start},{end},ALLSTARS,,0,0,0,,{text}")
    return lines
