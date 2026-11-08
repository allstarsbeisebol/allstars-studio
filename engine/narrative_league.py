"""Ilustração editorial sem texto para histórias de fundação de ligas.

Interpretação cinematográfica conceptual de uma reunião de organizadores
do beisebol no século XX; NÃO é retrato fiel de Rube Foster nem fotografia.
"""
import math,random
from PIL import Image,ImageDraw,ImageFilter

W,H=1080,1180
NAVY=(8,22,44);INK=(5,15,28);GOLD=(240,192,64)
PAPER=(227,204,157);RED=(181,45,62);SKIN=(106,68,53)

def person(d,x,y,scale=1.0,foreground=False):
    """Figura ilustrativa adulta em traje de época, não retrato de indivíduo."""
    s=scale
    head=(x-43*s,y-196*s,x+45*s,y-98*s)
    if foreground:
        d.ellipse((x-67*s,y-218*s,x+70*s,y-84*s),fill=(43,35,34,245))
    d.ellipse(head,fill=(116,75,54,255),outline=(224,170,117,235),width=max(2,int(s*4)))
    # Cabelo, pescoço, paletó, camisa e gravata; sem traços faciais atribuídos.
    d.pieslice((x-47*s,y-206*s,x+47*s,y-131*s),185,355,fill=(26,24,27,255))
    d.polygon([(x-23*s,y-101*s),(x+27*s,y-101*s),(x+40*s,y-45*s),(x-36*s,y-43*s)],fill=(127,82,61,255))
    d.polygon([(x-66*s,y-66*s),(x+62*s,y-70*s),(x+119*s,y+140*s),
               (x-121*s,y+140*s)],fill=(17,37,62,255),outline=(106,139,156,160))
    d.polygon([(x-36*s,y-60*s),(x,y+74*s),(x+37*s,y-60*s),(x,y-25*s)],fill=(236,227,207,250))
    d.polygon([(x-12*s,y-50*s),(x+10*s,y-50*s),(x+19*s,y+43*s),(x-2*s,y+80*s),(x-17*s,y+43*s)],fill=(149,43,55,255))
    d.line((x-84*s,y-11*s,x-122*s,y+80*s),fill=(92,110,124,220),width=max(3,int(10*s)))
    d.line((x+84*s,y-8*s,x+132*s,y+75*s),fill=(92,110,124,220),width=max(3,int(10*s)))

def league_scene(ep,index=0):
    """Produces unique narrative art on a 1080x1180 RGBA layer."""
    from story_art import art_key
    k=art_key(ep,index)
    rng=random.Random(int(k[:15],16))
    frame=Image.new("RGBA",(W,H),(*INK,255))
    bg=Image.new("RGBA",(W,H),(0,0,0,0))
    bd=ImageDraw.Draw(bg,"RGBA")
    # Historical interior with a playing field beyond the windows.
    for x0 in (130,415,700):
        x1=x0+215
        bd.rounded_rectangle((x0,95,x1,515),radius=13,fill=(38,65,83,245),outline=(189,145,81,180),width=11)
        bd.rectangle((x0+15,109,x1-15,490),fill=(60,92,102,255))
        bd.polygon([(x0+15,390),(x1-15,330),(x1-15,490),(x0+15,490)],
                   fill=(63,93,76,255))
        bd.line((x0+16,378,x1-15,340),fill=(215,204,160,130),width=8)
        for j in range(9):
            px=x0+26+j*20
            py=415+rng.randrange(0,70)
            bd.ellipse((px-4,py-7,px+5,py+3),fill=(13,30,39,180))
        bd.line((x0+115,95,x0+115,514),fill=(22,37,48,255),width=14)
        bd.line((x0,292,x1,292),fill=(22,37,48,255),width=14)
    bd.rectangle((0,0,W,110),fill=(16,32,49,255))
    for x in range(0,W,120):
        bd.line((x,45,x+90,45),fill=(213,167,91,76),width=5)
    bd.polygon([(12,530),(1074,530),(W,H),(0,H)],fill=(42,35,34,230))
    bg=bg.filter(ImageFilter.GaussianBlur(3))
    frame.alpha_composite(bg)
    # Golden light rays from the windows to make the meeting visually legible.
    rays=Image.new("RGBA",(W,H),(0,0,0,0))
    rd=ImageDraw.Draw(rays,"RGBA")
    rd.polygon([(220,180),(360,180),(790,1140),(300,1180)],fill=(246,184,102,25))
    rd.polygon([(760,160),(850,160),(1070,1050),(740,980)],fill=(236,199,127,20))
    frame.alpha_composite(rays.filter(ImageFilter.GaussianBlur(47)))
    d=ImageDraw.Draw(frame,"RGBA")
    # Figure group standing behind the table, materialising a decision-making scene.
    person(d,198,576,.80)
    person(d,856,562,.80)
    person(d,655,585,.83)
    # Central figure as illustrated ORGANIZER, not a biographical portrait.
    person(d,420,610,1.22,foreground=True)
    # Foreground table: perspective + nonverbal charter, ball and simple field sketch.
    d.polygon([(58,760),(975,760),(1090,1180),(-30,1180)],
              fill=(67,44,31,250),outline=(188,134,74,235))
    d.line((65,778,980,778),fill=(248,202,126,130),width=12)
    for dy in (884,970,1065):
        d.line((0,dy,1080,dy+14),fill=(17,30,39,110),width=7)
    # Charter on the table: blank paper, original mark without fictitious text.
    d.polygon([(306,795),(820,827),(762,1112),(249,1069)],fill=(*PAPER,245),
              outline=(248,219,161,255))
    d.polygon([(325,827),(796,855),(744,1088),(279,1042)],fill=(243,218,169,180))
    d.polygon([(549,858),(678,933),(547,1042),(408,938)],
              outline=(64,97,89,140),fill=(193,197,154,32))
    d.line((413,940,679,937),fill=(117,108,80,145),width=5)
    d.line((544,861,546,1040),fill=(117,108,80,145),width=5)
    for j in range(3):
        d.ellipse((325+j*140,849+j*42,339+j*140,865+j*42),
                  fill=(126,85,56,215))
    # Gloved hand touching the paper, theatrical action not a claim of photo.
    d.line((400,688,464,831),fill=(22,45,68,255),width=64)
    d.ellipse((437,809,505,855),fill=(130,84,61,255),outline=(223,168,120,200),width=4)
    # Vintage baseball as secondary symbol, not floating random icon.
    d.ellipse((830,924,992,1089),fill=(235,220,182,245),outline=(118,72,52,255),width=7)
    d.arc((845,940,937,1070),-55,105,fill=(*RED,245),width=7)
    d.arc((892,937,979,1072),80,265,fill=(*RED,245),width=7)
    # Warm editorial vignette, never stamps or typography in scene.
    corners=Image.new("RGBA",(W,H),(0,0,0,0))
    cd=ImageDraw.Draw(corners,"RGBA")
    cd.rectangle((0,0,70,H),fill=(5,16,35,105))
    cd.rectangle((W-70,0,W,H),fill=(5,16,35,105))
    frame.alpha_composite(corners.filter(ImageFilter.GaussianBlur(55)))
    return frame
