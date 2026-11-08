"""Composição editorial inédita, guiada pelo roteiro e assunto.

Sem API de imagem paga: esta opção entrega uma ILUSTRAÇÃO GRÁFICA contextual,
não finge ser anime premium nem retrato histórico. Cada episódio recebe cenas
próprias com prova de origem (id/roteiro/tema), nunca uma capa em cache.
"""
from __future__ import annotations
import hashlib, math, random, re
from PIL import Image, ImageDraw, ImageFilter, ImageFont

NAVY=(8,24,54); BLUE=(49,95,172); RED=(206,35,62); GOLD=(240,192,64)
WHITE=(247,249,255)
W,H=1080,1180

def font(size):
    for p in ("/usr/share/fonts/truetype/barlow/BarlowCondensed-ExtraBold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:return ImageFont.truetype(p,size)
        except OSError:pass
    return ImageFont.load_default()

def lines_for(draw,text,max_width,size=48,limit=2):
    f=font(size);lines=[];current=""
    for word in re.sub(r"\\s+"," ",str(text).strip()).split():
        attempt=(current+" "+word).strip()
        if current and draw.textbbox((0,0),attempt,font=f)[2]>max_width:
            lines.append(current);current=word
        else:current=attempt
    if current:lines.append(current)
    return lines[:limit],f

def classify(ep):
    data=" ".join(str(ep.get(x,"")) for x in ("subject","athlete","title","hook","narration","art_direction"))
    text=data.casefold()
    if any(x in text for x in ("no-hitter","sem rebatida","perfect game","jogo perfeito","strikeout","arremess")):return "arremesso"
    if any(x in text for x in ("home run","homerun","rebatida","rebatedor","hit","batedor")):return "rebatida"
    if any(x in text for x in ("latino","latina","porto rico","puerto rico","caribe","japones","afro")):return "legado"
    if any(x in text for x in ("lesão","lesao","acidente","supera","volta","recupera","lesion")):return "retorno"
    if any(x in text for x in ("contrato","troca","free agent","salário","salario","justiça","justica","direitos")):return "contrato"
    if any(x in text for x in ("regra","arbitr","física","fisica","curva","velocidade")):return "explicacao"
    if any(x in text for x in ("lista","maiores","top ","cinco","5 jogadores","ranking")):return "ranking"
    return "cronica"

def year_or_number(text):
    m=re.search(r"\\b(?:18|19|20)\\d{2}\\b",text)
    if m:return m.group(0)
    m=re.search(r"\\b(?:3[.,]?000|[1-9]\\d{2,3})\\b",text)
    return m.group(0) if m else None

def art_key(ep,index):
    # Id da execução torna cada produção original, inclusive se o assunto se repetir.
    base="|".join(str(ep.get(k,"")) for k in ("id","episode_number","subject","title","hook","art_direction"))
    base+="|"+str(index)
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def create_context_art(ep,index=0):
    seed=art_key(ep,index)
    rng=random.Random(int(seed[:16],16))
    kind=classify(ep)
    panel=Image.new("RGBA",(W,H),(*NAVY,255))
    d=ImageDraw.Draw(panel,"RGBA")
    # Halo de cor específico por história, sem imagens externas ou elementos reutilizados.
    accents=[BLUE,RED,GOLD]
    accent=accents[int(seed[0],16)%3]
    backdrop=Image.new("RGBA",(W,H),(0,0,0,0));bd=ImageDraw.Draw(backdrop,"RGBA")
    for j in range(6):
        x=rng.randint(-160,1200);y=rng.randint(-100,1100);radius=rng.randint(140,420)
        bd.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(*accents[j%3],rng.randint(22,65)))
    panel.alpha_composite(backdrop.filter(ImageFilter.GaussianBlur(120)))
    d=ImageDraw.Draw(panel,"RGBA")
    for i in range(24):
        x=rng.randrange(-250,1200);y=rng.randrange(0,1100)
        d.line((x,y,x+rng.randint(160,500),y-rng.randint(100,440)),
               fill=(*WHITE,rng.randint(10,38)),width=rng.randint(2,9))
    # História impressa como quadros autorais, não um poster-base compartilhado.
    d.rounded_rectangle((86,84,996,955),radius=52,fill=(3,15,36,150),outline=(*GOLD,175),width=4)
    d.rectangle((98,100,982,120),fill=(*accent,235))
    for j in range(14):
        x=105+j*66
        d.polygon([(x,128),(x+40,128),(x+10,155)],fill=(RED if j%4==0 else WHITE)+(35,))
    center=(540,490);x,y=center
    if kind=="arremesso":
        # Zona de strike, bola e curva de trajetória.
        d.rounded_rectangle((276,244,804,740),radius=18,outline=(*WHITE,195),width=12)
        for v in (420,564):d.line((278,v,802,v),fill=(*WHITE,90),width=5)
        for v in (452,628):d.line((v,244,v,740),fill=(*WHITE,90),width=5)
        points=[(170+i*12,int(720-310*math.sin(i/83*math.pi)+20*math.sin(i/7))) for i in range(83)]
        d.line(points,fill=(*GOLD,210),width=16,joint="curve")
        bx,by=points[-1];d.ellipse((bx-54,by-54,bx+54,by+54),fill=WHITE,outline=(*RED,220),width=7)
    elif kind=="rebatida":
        d.line((265,780,730,250),fill=(*GOLD,255),width=66)
        d.line((265,780,730,250),fill=(*WHITE,190),width=19)
        for j in range(7):
            a=j/7*2*math.pi
            bx=x+270*math.cos(a);by=y+225*math.sin(a)
            d.line((x,y,bx,by),fill=(*RED,160),width=10)
        d.ellipse((595,200,895,500),fill=WHITE,outline=(*RED,210),width=15)
        d.arc((635,235,760,465),-80,100,fill=RED,width=11);d.arc((725,235,850,465),80,270,fill=RED,width=11)
    elif kind in ("legado","ranking"):
        count=5 if kind=="ranking" else 3
        for i in range(count):
            xx=186+i*(720//count);yy=278+i%2*85
            d.rounded_rectangle((xx,yy,xx+180,yy+305),radius=22,fill=(*BLUE,210),outline=(*GOLD,210),width=5)
            d.text((xx+44,yy+77),str(i+1).zfill(2),font=font(90),fill=WHITE)
            d.ellipse((xx+62,yy+202,xx+125,yy+265),fill=(*GOLD,230))
    elif kind=="retorno":
        d.arc((175,180,905,860),35,310,fill=(*GOLD,240),width=45)
        d.polygon([(758,198),(918,215),(849,351)],fill=(*GOLD,250))
        for i in range(10):
            yy=290+i*43;d.line((320,yy,740,yy-35),fill=(*WHITE,65+i*8),width=5)
        d.ellipse((417,375,667,625),fill=(*RED,225),outline=WHITE,width=14)
    elif kind=="contrato":
        d.polygon([(320,170),(710,220),(760,795),(264,752)],fill=(*WHITE,235))
        for i in range(8):d.line((335,320+i*49,667,330+i*51),fill=(*NAVY,130),width=9)
        d.line((370,698,654,674),fill=(*RED,220),width=20)
        d.ellipse((680,615,850,785),fill=(*GOLD,220))
    elif kind=="explicacao":
        for radius in (180,260,350):d.arc((x-radius,y-radius,x+radius,y+radius),200,340,fill=(*GOLD,210),width=12)
        d.line((245,790,790,265),fill=WHITE,width=13)
        d.ellipse((360,325,590,555),fill=WHITE,outline=RED,width=17)
        for i in range(5):d.line((760+i*13,370,835+i*15,680),fill=(*RED,180),width=9)
    else:
        # Cronologia jornalística: documento original de contexto, com ano da narrativa.
        for j in range(3):
            x0=180+j*185;y0=270+j%2*78
            d.rounded_rectangle((x0,y0,x0+250,y0+390),radius=14,fill=(*WHITE,230),outline=(*GOLD,185),width=6)
            for k in range(5):d.line((x0+33,y0+120+44*k,x0+210,y0+120+44*k),fill=(*NAVY,115),width=10)
            d.rectangle((x0+28,y0+28,x0+207,y0+92),fill=(RED if j%2==0 else BLUE)+(220,))
    # Contexto textual factual, vindo SOMENTE do episódio, sem inserir estatísticas inventadas.
    note=year_or_number(" ".join(str(ep.get(k,"")) for k in ("subject","title","hook","narration")))
    if note:
        d.rounded_rectangle((100,835,385,940),radius=13,fill=(*GOLD,235))
        d.text((126,849),note,font=font(63),fill=NAVY)
    # Cenas diferem entre si e continuam associadas ao tema pesquisado.
    headline=str(ep.get("hook") if index==0 else (ep.get("screens") or [ep.get("title","")])[min(index-1,len(ep.get("screens") or [1])-1)])
    short=headline or str(ep.get("title") or ep.get("subject") or "")
    sentences,f=lines_for(d,short.upper(),830,38,2)
    d.rounded_rectangle((110,972,968,1144),radius=20,fill=(3,12,29,240),outline=(*accent,190),width=4)
    for j,line in enumerate(sentences):
        d.text((145,997+j*54),line,font=f,fill=WHITE)
    panel.info["allstars_art_key"]=seed
    return panel

def art_metadata(ep,index=0):
    return {"generation_key":art_key(ep,index),"visual_type":"original_contextual_vector_art",
            "story_mode":classify(ep),"art_direction":str(ep.get("art_direction") or ep.get("title") or "")[:600],
            "episode_id":str(ep.get("id") or ep.get("episode_number") or ""),
            "rights":"Composição gráfica criada localmente pelo ALLSTARS Studio; não é foto documental nem arte anime premium."}
