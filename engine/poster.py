"""Compositor editorial ALLSTARS 9:16. Fotos apenas com licença documentada.

Usa exclusivamente o logotipo oficial de brand/logo.png ou brand/logo.b64.
Nenhuma fotografia é inventada ou apresentada como registro histórico.
"""
from __future__ import annotations
import base64, io, json, random, re, unicodedata
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from comic_hero import cartoon_player
from anime_assets import hero_from_approved_asset

ROOT = Path(__file__).resolve().parents[1]
W, H = 1080, 1920
brand = json.loads((ROOT/"brand/identity.json").read_text(encoding="utf-8"))
colors = brand["colors"]
def color(name): return tuple(bytes.fromhex(colors[name][1:]))
ROYAL, NAVY, RED, GOLD, WHITE = [color(x) for x in ("royal_blue","navy","red","gold","white")]
INK = (4, 14, 33)

def face(size, condensed=True):
    paths = ([
       "/usr/share/fonts/truetype/barlow/BarlowCondensed-ExtraBold.ttf",
       "/usr/share/fonts/truetype/oswald/Oswald-Bold.ttf",
       "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
       "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ] if condensed else [
       "/usr/share/fonts/truetype/barlow/Barlow-Bold.ttf",
       "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ])
    for path in paths:
        if Path(path).is_file(): return ImageFont.truetype(path,size)
    return ImageFont.load_default()

def slug(text):
    t=unicodedata.normalize("NFKD",str(text)).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+","-",t).strip("-")

def official_logo():
    path=ROOT/"brand/logo.png"
    if path.is_file():
        with Image.open(path) as im: return im.convert("RGBA")
    path=ROOT/"brand/logo.b64"
    if path.is_file():
        content=base64.b64decode(path.read_text(encoding="ascii").strip())
        with Image.open(io.BytesIO(content)) as im: return im.convert("RGBA")
    raise FileNotFoundError("Logo oficial não cadastrada. Adicione brand/logo.png ou brand/logo.b64.")

def licensed_photo(episode):
    athlete=slug(episode.get("athlete",""))
    path=ROOT/"assets/athletes"/(athlete+".jpg")
    record=ROOT/"assets/athletes"/(athlete+".license.json")
    if not (path.is_file() and record.is_file()): return None
    try:
        metadata=json.loads(record.read_text(encoding="utf-8"))
        if metadata.get("approved_for_publication") is not True or not metadata.get("source_url") or not metadata.get("license"): return None
        with Image.open(path) as src:
            src=ImageOps.exif_transpose(src).convert("RGB")
            scale=max(W/src.width,1270/src.height)
            src=src.resize((round(src.width*scale),round(src.height*scale)),Image.Resampling.LANCZOS)
            x=(src.width-W)//2;y=int(max(0,(src.height-1270)*0.3))
            return ImageEnhance.Contrast(src.crop((x,y,x+W,y+1270))).enhance(1.15)
    except (OSError,ValueError,TypeError,KeyError):
        # Foto/manifesto ilegível: recuperar com cartoon, sem gerar tela vazia.
        return None

def gradient():
    strip=Image.new("RGB",(1,H))
    pix=strip.load()
    for y in range(H):
        t=y/H
        pix[0,y]=tuple(int(INK[i]*(1-t)+NAVY[i]*t*0.8) for i in range(3))
    return strip.resize((W,H)).convert("RGBA")

def draw_stadium(base,seed):
    randomizer=random.Random(seed)
    layer=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(layer,"RGBA")
    # Holofotes e arquibancadas desfocadas com aparência de foto noturna.
    for i in range(2400):
        x=randomizer.randrange(W);y=randomizer.randrange(145,1230)
        r=randomizer.randint(3,14)
        c=randomizer.choice([WHITE,GOLD,ROYAL,(156,180,213),(209,91,103)])
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*c,randomizer.randint(12,70)))
    d.arc((-220,120,1320,1110),190,355,fill=(*WHITE,68),width=22)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(15)))
    lights=Image.new("RGBA",(W,H),(0,0,0,0));ld=ImageDraw.Draw(lights,"RGBA")
    ld.polygon([(50,140),(180,140),(660,1120),(490,1150)],fill=(253,232,193,18))
    ld.polygon([(1030,130),(855,170),(390,1120),(590,1180)],fill=(240,246,255,18))
    for x in (120,240,860,975):
        ld.ellipse((x-45,165,x+45,255),fill=(255,235,196,110))
    base.alpha_composite(lights.filter(ImageFilter.GaussianBlur(36)))

def illustrated_player(base):
    # Ilustração estilizada original, sem fingir ser fotografia do jogador.
    layer=Image.new("RGBA",(W,1210),(0,0,0,0));d=ImageDraw.Draw(layer,"RGBA")
    shadow=(4,19,44,244);edge=(101,164,240,130)
    d.line((730,120,485,715),fill=(235,203,143,176),width=30)
    d.line((522,615,317,365),fill=shadow,width=110)
    d.ellipse((245,286,382,423),fill=shadow,outline=edge,width=8)
    d.polygon([(423,445),(660,440),(875,705),(820,1200),(315,1180),(285,740)],fill=(17,43,88,255))
    d.ellipse((390,170,667,490),fill=shadow,outline=edge,width=9)
    d.polygon([(398,238),(560,146),(737,246),(769,310),(408,306)],fill=(22,63,128,255))
    d.line((640,565,1030,832),fill=shadow,width=120)
    d.line((650,565,1030,832),fill=edge,width=12)
    d.ellipse((977,778,1072,874),fill=(235,242,255,213))
    for i in range(7):
        x=420+i*38;d.line((x,650,x+10,1090),fill=(*ROYAL,90),width=6)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(20)),(0,130))
    base.alpha_composite(layer,(0,130))

def thematic_hero(base,episode):
    """Ilustração editorial temática: bola, diamante e estádio, sem atleta falso."""
    layer=Image.new("RGBA",(W,1120),(0,0,0,0))
    d=ImageDraw.Draw(layer,"RGBA")
    kind=episode.get("content_type","tema")
    d.ellipse((180,155,910,885),fill=(3,15,38,130),outline=(*ROYAL,145),width=13)
    d.polygon([(530,180),(845,520),(530,865),(215,520)],fill=(*ROYAL,60),outline=(*GOLD,180),width=12)
    d.line((525,188,846,520,525,860,212,520,525,188),fill=(*WHITE,110),width=7,joint="curve")
    # Bola de beisebol original, desenhada como elemento esportivo central.
    d.ellipse((325,240,775,690),fill=(247,248,241,245),outline=(*NAVY,255),width=22)
    d.arc((355,258,605,672),-82,79,fill=(*RED,255),width=16)
    d.arc((495,258,746,672),103,262,fill=(*RED,255),width=16)
    for j in range(6):
        y=315+j*47
        d.line((410-j*8,y,443-j*4,y+18),fill=(*RED,220),width=7)
        d.line((643+j*7,y,671+j*3,y-17),fill=(*RED,220),width=7)
    # Faixas temáticas, com destaque ao formato escolhido.
    label={"tema":"HISTÓRIA DO BEISEBOL","noticia":"NOTÍCIA & CONTEXTO",
           "lista":"NÚMEROS & HISTÓRIAS","explicativo":"ENTENDA O BEISEBOL"}.get(kind,"ALÉM DO JOGO")
    f=face(46)
    tw=d.textbbox((0,0),label,font=f)[2]
    d.rounded_rectangle((540-tw//2-34,735,540+tw//2+34,825),radius=20,
                        fill=(*NAVY,235),outline=(*GOLD,210),width=4)
    d.text((540-tw//2,749),label,font=f,fill=WHITE)
    base.alpha_composite(layer,(0,185))
    return True

def add_hero(base,episode):
    if episode.get("content_type","atleta") not in ("atleta",):
        return thematic_hero(base,episode)
    curated=hero_from_approved_asset(episode)
    if curated is not None:
        image,metadata=curated
        fade=Image.new("L",(1,image.height),255)
        for y in range(690,image.height):
            fade.putpixel((0,y),int(255*max(0,(image.height-y)/(image.height-690))))
        image.putalpha(fade.resize(image.size))
        base.alpha_composite(image,(0,145))
        return True
    photo=licensed_photo(episode)
    if photo is None:
        # Cartoon original com rosto/uniforme completos. Não retrato fiel.
        base.alpha_composite(cartoon_player(episode.get("athlete","Atleta"),episode.get("episode_number",0)),(0,125))
        return False
    overlay=photo.convert("RGBA")
    film=Image.new("RGBA",overlay.size,(*NAVY,36))
    overlay=Image.alpha_composite(overlay,film)
    opacity=Image.new("L",(1,1270),255)
    for y in range(620,1270):opacity.putpixel((0,y),int(255*max(0,(1270-y)/650)))
    overlay.putalpha(opacity.resize((W,1270)))
    base.alpha_composite(overlay,(0,145))
    return True

def paint(draw,top,bottom,hue,seed):
    r=random.Random(seed)
    draw.polygon([(0,top+r.randint(10,55)),(W,top-r.randint(4,32)),(W,bottom-r.randint(5,38)),(0,bottom+r.randint(7,40))],fill=(*hue,249))
    for i in range(110):
        x=r.randint(0,W); y=r.choice([top,bottom])+r.randint(-25,25)
        draw.line((x,y,min(W,x+r.randint(15,130)),y+r.randint(-8,8)),fill=(*hue,r.randint(55,235)),width=r.randint(2,9))

def headline_fit(message):
    """Tipografia grande, mas dentro da faixa editorial e sem cortar palavras."""
    draw=ImageDraw.Draw(Image.new("RGB",(1,1)))
    original=re.sub(r"\s+"," ",str(message).upper()).strip()
    text=original[:135]
    for size in range(138,41,-3):
        font=face(size)
        lines=[];line=""
        for word in text.split():
            attempt=(line+" "+word).strip()
            if line and draw.textbbox((0,0),attempt,font=font)[2]>920:
                lines.append(line);line=word
            else:line=attempt
        if line:lines.append(line)
        max_width=max([draw.textbbox((0,0),line,font=font)[2] for line in lines] or [0])
        if len(lines)<=4 and max_width<=920 and int(size*1.08)*len(lines)<=345:
            return font,lines
    # Apenas títulos extremamente longos recebem indicação visual de corte.
    font=face(43)
    lines=[];line=""
    for word in text.split():
        attempt=(line+" "+word).strip()
        if line and draw.textbbox((0,0),attempt,font=font)[2]>920:
            lines.append(line);line=word
        else:line=attempt
    if line:lines.append(line)
    if len(lines)>4:
        lines=lines[:4]
        while draw.textbbox((0,0),lines[-1]+"…",font=font)[2]>920:
            lines[-1]=" ".join(lines[-1].split()[:-1])
        lines[-1]+="…"
    return font,lines

def poster(episode,headline=None,index=0,total=1):
    base=gradient();draw_stadium(base,2026+index)
    has_photo=add_hero(base,episode)
    dark=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(dark,"RGBA")
    for y in range(850,1740,4):
        alpha=int(min(235,(y-850)/890*238))
        d.rectangle((0,y,W,y+3),fill=(*INK,alpha))
    base.alpha_composite(dark)
    art=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(art,"RGBA")
    paint(d,22,145,NAVY,10+index)
    d.line((0,105,110,105),fill=GOLD,width=8)
    d.text((128,38),"ALÉM DO JOGO",font=face(76),fill=WHITE,stroke_width=1,stroke_fill=INK)
    tag="ALLSTARS"
    ft=face(43)
    right=W-d.textbbox((0,0),tag,font=ft)[2]-48
    d.text((right,68),tag,font=ft,fill=GOLD)
    text=headline or episode.get("cover_headline") or episode.get("title") or "ALÉM DO JOGO"
    f,lines=headline_fit(text)
    lh=int(f.size*1.08)
    # A faixa central y=930..1150 é exclusiva das legendas.
    # O título da cena fica abaixo de y=1240, sem disputar a leitura.
    start=1230+max(0,(355-lh*len(lines))//2)
    paint(d,start-50,start+len(lines)*lh+65,NAVY,18+index)
    if len(lines)>=3:paint(d,start+2*lh-26,start+len(lines)*lh+57,RED,73+index)
    for i,line in enumerate(lines):
        width=d.textbbox((0,0),line,font=f)[2]
        x=(W-width)//2;y=start+i*lh
        d.text((x+5,y+8),line,font=f,fill=(3,9,24),stroke_width=3,stroke_fill=INK)
        d.text((x,y),line,font=f,fill=GOLD if i>=len(lines)-max(1,len(lines)//2) else WHITE,stroke_width=3,stroke_fill=INK)
    d.line((72,1663,1007,1663),fill=GOLD,width=5)
    label=str(episode.get("subject") or episode.get("athlete","HISTÓRIA DO BEISEBOL")).upper()
    if index:label+=f"  ·  CENA {index:02}/{total:02}"
    lf=face(42,False)
    while d.textbbox((0,0),label,font=lf)[2]>900 and lf.size>23:lf=face(lf.size-2,False)
    d.text(((W-d.textbbox((0,0),label,font=lf)[2])//2,1672),label,font=lf,fill=WHITE)
    base.alpha_composite(art)
    logo=official_logo()
    # Aumenta com proporção original preservada, sem recriar a marca.
    scale=min(460/max(1,logo.width),145/max(1,logo.height))
    if abs(scale-1)>0.01:
        logo=logo.resize((max(1,round(logo.width*scale)),max(1,round(logo.height*scale))),Image.Resampling.LANCZOS)
    x=(W-logo.width)//2;y=1742
    shade=Image.new("RGBA",(W,H),(0,0,0,0))
    sd=ImageDraw.Draw(shade,"RGBA")
    sd.rounded_rectangle((x-38,y-18,x+logo.width+38,y+logo.height+26),radius=14,fill=(*INK,205))
    base.alpha_composite(shade);base.alpha_composite(logo,(x,y))
    texture=Image.new("RGBA",(W,H),(0,0,0,0));td=ImageDraw.Draw(texture,"RGBA")
    rng=random.Random(921+index)
    for i in range(2600):
        x=rng.randrange(W);y=rng.randrange(H)
        if y>1720 and 290<x<800:continue
        td.point((x,y),fill=(255,255,255,rng.randrange(1,22)) if i%2 else (0,0,0,rng.randrange(1,22)))
    td.arc((-220,1580,300,2100),290,60,fill=(*ROYAL,95),width=18)
    base.alpha_composite(texture)
    return base.convert("RGB")
