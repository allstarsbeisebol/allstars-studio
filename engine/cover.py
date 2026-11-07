#!/usr/bin/env python3
"""Capa 9:16 da série Além do Jogo, baseada na Bíblia Visual ALLSTARS 2026.

Utiliza APENAS o logotipo oficial em brand/logo.png quando presente.
Fotos dos atletas: assets/athletes/<slug>.jpg, com direitos registrados no manifesto.
Sem foto aprovada, utiliza arte editorial genérica (não representa o atleta).
"""
import argparse, json, math, random, re, unicodedata
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

P=argparse.ArgumentParser()
P.add_argument("--episode",default="data/episode.json")
P.add_argument("--output",default="output/capa.png")
args=P.parse_args()
ROOT=Path(__file__).resolve().parents[1]
ep=json.loads(Path(args.episode).read_text(encoding="utf-8"))
brand=json.loads((ROOT/"brand/identity.json").read_text(encoding="utf-8"))
colors=brand["colors"]
def rgb(name):return tuple(bytes.fromhex(colors[name][1:]))
ROYAL,NAVY,RED,GOLD,WHITE=(rgb(n) for n in ("royal_blue","navy","red","gold","white"))
W,H=1080,1920
def font(size,bold=True):
    family=["/usr/share/fonts/truetype/barlow/BarlowCondensed-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    for path in family:
        if Path(path).exists():return ImageFont.truetype(path,size)
    return ImageFont.load_default()
def slug(s):
    s=unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+","-",s).strip("-")
def center_crop(im,w,h):
    ratio=max(w/im.width,h/im.height)
    im=im.resize((round(im.width*ratio),round(im.height*ratio)),Image.Resampling.LANCZOS)
    x=(im.width-w)//2;y=(im.height-h)//2
    return im.crop((x,y,x+w,y+h))
def linewrap(draw,text,ft,maxwidth):
    lines=[];line=""
    for word in text.split():
        test=(line+" "+word).strip()
        if draw.textbbox((0,0),test,font=ft)[2]>maxwidth and line:
            lines.append(line);line=word
        else:line=test
    if line:lines.append(line)
    return lines
def fit(draw,text,maxwidth,maxlines=4):
    for size in range(116,48,-4):
        ft=font(size)
        lines=linewrap(draw,text,ft,maxwidth)
        if len(lines)<=maxlines:return ft,lines
    return font(50),linewrap(draw,text,font(50),maxwidth)

# Gradiente escuro, com estádio ilustrativo — sem inventar imagem documental.
strip=Image.new("RGB",(1,H))
p=strip.load()
for y in range(H):
    t=y/H
    p[0,y]=(max(0,min(255,int(NAVY[0]*(1-t)+ROYAL[0]*t*.45))),
            max(0,min(255,int(NAVY[1]*(1-t)+ROYAL[1]*t*.48))),
            max(0,min(255,int(NAVY[2]*(1-t)+ROYAL[2]*t*.62))))
im=strip.resize((W,H)).convert("RGBA")
crowd=Image.new("RGBA",(W,H),(0,0,0,0))
cd=ImageDraw.Draw(crowd,"RGBA")
rng=random.Random(2026)
for i in range(950):
    x=rng.randrange(W);y=rng.randrange(150,1260)
    size=rng.randrange(3,18)
    c=(220,224,239,rng.randrange(8,35)) if i%3 else (240,192,64,rng.randrange(8,32))
    cd.ellipse((x-size,y-size,x+size,y+size),fill=c)
crowd=crowd.filter(ImageFilter.GaussianBlur(18))
im=Image.alpha_composite(im,crowd)

athlete=slug(ep.get("athlete",""))
photo=ROOT/"assets/athletes"/(athlete+".jpg")
licensed=ROOT/"assets/athletes"/(athlete+".license.json")
has_photo=False
if photo.is_file() and licensed.is_file():
    record=json.loads(licensed.read_text(encoding="utf-8"))
    if record.get("approved_for_publication") is True and record.get("source_url") and record.get("license"):
        with Image.open(photo) as source:
            portrait=center_crop(source.convert("RGB"),W,1280).convert("RGBA")
            shade=Image.new("RGBA",portrait.size,(0,0,0,0))
            sd=ImageDraw.Draw(shade,"RGBA")
            for y in range(800,1280):
                sd.rectangle((0,y,W,y+1),fill=(*NAVY,int((y-800)/480*240)))
            portrait=Image.alpha_composite(portrait,shade)
            im.alpha_composite(portrait,(0,120))
            has_photo=True

art=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(art,"RGBA")
# Painéis inclinados e textura de pincel (produzidos pelo próprio código).
def stroke(y,h,color,seed):
    r=random.Random(seed)
    pts=[(0,y+r.randint(20,65)),(W,y-r.randint(10,35)),(W,y+h-r.randint(10,50)),(0,y+h+r.randint(0,35))]
    d.polygon(pts,fill=(*color,238))
    for j in range(55):
        px=r.randint(0,W);py=r.choice([y,y+h])+r.randint(-25,25)
        d.line([(px,py),(min(W,px+r.randint(20,160)),py+r.randint(-8,8))],fill=(*color,r.randint(80,215)),width=r.randint(2,11))
stroke(25,120,NAVY,1)
d.line((0,96,180,96),fill=GOLD,width=9)
d.line((900,96,1080,96),fill=GOLD,width=9)
d.text((80,40),"ALÉM DO JOGO",font=font(70),fill=WHITE)
number=ep.get("episode_number",ep.get("number",""))
try:number=int(number)
except (ValueError,TypeError):number=None
tag=f"EP. {number:02d}" if number is not None else "ALLSTARS"
d.text((762,45),tag,font=font(54),fill=GOLD)

if not has_photo:
    # Representação simbólica assumidamente ilustrativa, sem fingir foto histórica.
    d.ellipse((265,220,805,760),fill=(18,36,73,255),outline=(*GOLD,170),width=8)
    d.line((400,750,760,280),fill=(*WHITE,200),width=30)
    d.ellipse((440,360,600,520),fill=(*WHITE,190))
    d.text((110,760),"ARTE EDITORIAL • SEM FOTO DE ARQUIVO",font=font(29),fill=GOLD)

stroke(960,375,NAVY,22)
stroke(1230,260,RED,33)
headline=ep.get("cover_headline") or ep.get("title") or ep.get("athlete","ALÉM DO JOGO")
headline=headline.upper().strip()
# Limitar a headline sem descaracterizar a mensagem; usa quebra automática.
ft,lines=fit(d,headline,900,5)
top=985
if len(lines)>4:top=950
for i,line in enumerate(lines[:5]):
    fill=GOLD if i>=max(1,len(lines)//2) else WHITE
    d.text((70,top+i*max(80,int(ft.size*1.05))),line,font=ft,fill=fill,stroke_width=2,stroke_fill=NAVY)
d.rectangle((70,1570,1010,1577),fill=GOLD)
d.text((74,1600),ep.get("athlete","").upper(),font=font(57),fill=WHITE)
d.text((74,1672),"SÉRIE DOCUMENTAL • BEISEBOL",font=font(28),fill=GOLD)

# Marca: obrigatoriamente reutiliza o arquivo oficial, sem redesenho.
logo=ROOT/"brand/logo.png"
if logo.is_file():
    with Image.open(logo) as src:
        src=src.convert("RGBA")
        src.thumbnail((540,160),Image.Resampling.LANCZOS)
        plate=(W-src.width)//2
        im=Image.alpha_composite(im,art)
        art=Image.new("RGBA",(W,H),(0,0,0,0))
        if src.getpixel((0,0))[3]==255:
            ad=ImageDraw.Draw(art,"RGBA");ad.rounded_rectangle((plate-22,1728,plate+src.width+22,1728+src.height+28),radius=16,fill=(*NAVY,240))
        art.alpha_composite(src,(plate,1742))
        ImageDraw.Draw(art).text((W//2-145,1878),"AQUI VOCÊ BRILHA!",font=font(25),fill=GOLD)
else:
    d.text((210,1790),"ALÉM DO JOGO",font=font(65),fill=WHITE)
    d.text((300,1870),"AQUI VOCÊ BRILHA!",font=font(30),fill=GOLD)

im=Image.alpha_composite(im,art).convert("RGB")
output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
im.save(output,optimize=True)
print("Capa:",output,"| foto aprovada:",has_photo,"| logo oficial:",logo.is_file())
