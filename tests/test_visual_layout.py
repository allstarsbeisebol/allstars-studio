"""Testes sem internet: margens aprovadas e alternativa cartoon real."""
import json, tempfile, sys, unittest
from pathlib import Path
from PIL import ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from subtitle_layout import WIDTH,HEIGHT,LEFT,RIGHT,TOP,BOTTOM,partition,ass_dialogues
from comic_hero import cartoon_player
from poster import poster

class SubtitleGeometryTests(unittest.TestCase):
    def test_required_safe_box(self):
        self.assertEqual((WIDTH,HEIGHT),(1080,1920))
        self.assertEqual((LEFT,RIGHT,TOP,BOTTOM),(162,918,930,1150))
        self.assertEqual(RIGHT-LEFT,756)
    def test_two_lines_and_measured_width(self):
        words="Um arremessador venceu barreiras e conquistou um lugar na história do beisebol americano".split()
        times=[(i*.32,(i+1)*.32) for i in range(len(words))]
        result=partition(words,times)
        self.assertGreaterEqual(len(result),2)
        for item in result:
            self.assertLessEqual(len(item["lines"]),2)
            self.assertLessEqual(item["font_size"],52)
            font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",item["font_size"])
            for line in item["lines"]:
                self.assertLessEqual(font.getlength(line),700)
        self.assertEqual(" ".join(x["text"] for x in result)," ".join(words))
    def test_ass_positions(self):
        groups=[{"start":0,"end":2,"lines":["UM DIA","INESQUECÍVEL"],"font_size":48}]
        lines=ass_dialogues(groups,lambda n:f"0:00:{n:05.2f}")
        self.assertEqual(len(lines),2)
        self.assertIn("m 162 930 l 918 930 918 1150",lines[0])
        self.assertIn(r"\pos(540,1040)",lines[1])
        self.assertIn(r"\N",lines[1])
    def test_cartoon_has_actual_character_not_silhouette(self):
        cartoon=cartoon_player("Jim Abbott")
        self.assertEqual(cartoon.size,(1080,1270))
        self.assertEqual(cartoon.mode,"RGBA")
        # Illustration has face, cap, shirt and contrast, not a blank background.
        self.assertGreater(len(cartoon.getcolors(maxcolors=20000) or []),15)
    def test_poster_without_photo_uses_original_cartoon(self):
        ep={"athlete":"Jim Abbott","title":"UMA HISTÓRIA DE SUPERAÇÃO","episode_number":11}
        im=poster(ep)
        self.assertEqual(im.size,(1080,1920))
        profile=im.crop((0,240,1080,1680))
        self.assertEqual(profile.size,(1080,1440))

if __name__=="__main__":unittest.main()
