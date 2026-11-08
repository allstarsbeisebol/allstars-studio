"""Arte cartoon original para cenas sem fotografia licenciada.

Personagem fictício de beisebol em estilo graphic-novel/anime, com feições
desenhadas, olhos, uniforme e corpo. Não sugere retrato fiel do atleta citado.
"""
from PIL import Image, ImageDraw, ImageFilter
import hashlib, math, random

def cartoon_player(athlete,scene=0):
    w,h=1080,1270
    seed=int.from_bytes(hashlib.sha256(str(athlete).encode()).digest()[:8],"big")
    rng=random.Random(seed)
    layer=Image.new("RGBA",(w,h),(0,0,0,0))
    d=ImageDraw.Draw(layer,"RGBA")
    ink=(5,17,42,255);royal=(49,95,172,255);red=(206,35,62,255)
    gold=(240,192,64,255);white=(235,241,251,255)
    skin=rng.choice([(192,135,96,255),(150,93,67,255),(221,164,122,255),(112,75,60,255)])
    shade=tuple(max(0,c-44) for c in skin[:3])+(255,)
    x=520+rng.randint(-55,55)
    # dramatic illustrated spotlight; no black shadow cutout
    flare=Image.new("RGBA",(w,h),(0,0,0,0));fd=ImageDraw.Draw(flare,"RGBA")
    fd.ellipse((x-380,95,x+350,1100),fill=(120,173,245,55))
    layer.alpha_composite(flare.filter(ImageFilter.GaussianBlur(60)))
    d=ImageDraw.Draw(layer,"RGBA")
    # batting equipment / bat kept behind fully illustrated player
    d.line((x+220,120,x+410,840),fill=ink,width=46)
    d.line((x+221,130,x+394,795),fill=(188,147,95,255),width=33)
    d.line((x+228,175,x+395,800),fill=(246,208,142,130),width=7)
    # athletic lower body trousers
    d.polygon([(x-252,975),(x+240,970),(x+255,1269),(x-60,1269),(x-78,1110),(x-150,1269),(x-360,1269)],
              fill=(211,220,230,255),outline=ink,width=14)
    d.line((x-82,1040,x-75,1260),fill=(49,95,172,220),width=16)
    d.line((x+205,1010,x+173,1270),fill=(49,95,172,220),width=15)
    # expressive action uniform, broad shoulders
    d.polygon([(x-220,610),(x-115,560),(x+122,556),(x+285,640),
               (x+245,1100),(x-270,1110)],fill=white)
    d.line((x-220,610,x-270,1110,x+245,1100,x+285,640),fill=ink,width=20,joint="curve")
    # red/royal jersey trim and seams
    d.line((x-145,580,x-125,1085),fill=royal,width=22)
    d.line((x+123,578,x+116,1083),fill=royal,width=21)
    d.line((x-95,635,x+80,960),fill=red,width=30)
    d.polygon([(x-238,630),(x-165,650),(x-282,870),(x-364,824)],fill=royal)
    d.polygon([(x+198,640),(x+277,628),(x+364,855),(x+255,888)],fill=red)
    # two dynamic arms with cartoon strokes
    d.line((x-215,705,x-350,470),fill=ink,width=119)
    d.line((x-215,705,x-350,470),fill=skin,width=89)
    d.ellipse((x-414,397,x-290,528),fill=skin,outline=ink,width=13)
    d.line((x+250,725,x+405,492),fill=ink,width=120)
    d.line((x+250,725,x+405,492),fill=skin,width=89)
    d.ellipse((x+343,420,x+469,535),fill=skin,outline=ink,width=13)
    # Fingertip/knuckle strokes distinguish hands from featureless circles.
    for delta in (0,20,40):
        d.arc((x+352+delta,442,x+420+delta,505),35,135,fill=shade,width=5)
    for delta in (0,17,34):
        d.arc((x-399+delta,417,x-333+delta,490),30,145,fill=shade,width=4)
    # neck and face (no silhouette)
    d.rounded_rectangle((x-75,517,x+85,652),radius=35,fill=shade,outline=ink,width=14)
    d.ellipse((x-168,228,x+173,570),fill=ink)
    d.ellipse((x-152,244,x+160,551),fill=skin)
    d.polygon([(x-132,396),(x-107,477),(x-27,530),(x+71,520),(x+138,439),
               (x+126,525),(x+52,572),(x-47,568),(x-139,514)],fill=shade)
    # Adult graphic-novel expression: focused eyes, angular brows and jaw.
    for offset in (-76,72):
        cx=x+offset
        brow_angle=-13 if offset<0 else 13
        d.line((cx-38,374+brow_angle,cx+39,371-brow_angle),fill=ink,width=15)
        d.ellipse((cx-25,398,cx+24,426),fill=white)
        d.ellipse((cx-13,398,cx+18,431),fill=ink)
        d.ellipse((cx-6,402,cx+4,411),fill=white)
    d.line((x+1,434,x-7,475,x+18,476),fill=shade,width=13)
    d.line((x-39,510,x+44,507),fill=ink,width=9)
    d.line((x-33,518,x+38,519),fill=(99,42,38,255),width=4)
    # comic shading and strong cheek structure
    for off in (-115,105):
        d.line((x+off-12,463,x+off+18,473),fill=(164,62,68,135),width=5)
    # cap with gold stripe and outlined visor
    d.pieslice((x-175,180,x+175,371),180,358,fill=royal,outline=ink,width=14)
    d.polygon([(x-194,300),(x+198,302),(x+340,370),(x+273,421),
               (x-130,394)],fill=royal)
    d.line((x-180,315,x+190,316,x+327,376),fill=ink,width=16)
    d.line((x-155,315,x+175,315),fill=gold,width=10)
    # stylized non-team star patch on cap and torso
    def star(cx,cy,r):
        pts=[]
        for i in range(10):
            a=-math.pi/2+i*math.pi/5
            length=r if i%2==0 else r*.43
            pts.append((cx+math.cos(a)*length,cy+math.sin(a)*length))
        d.polygon(pts,fill=gold)
        d.line(pts+[pts[0]],fill=ink,width=6,joint="curve")
    star(x,277,43)
    star(x+5,767,63)
    # ink linework + screenprint shine
    d.arc((x-218,590,x+275,1120),10,130,fill=(13,51,104,135),width=9)
    d.line((x-258,1091,x+243,1085),fill=ink,width=14)
    return layer
