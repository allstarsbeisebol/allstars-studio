"""QA de conteúdo contextual, marca oficial e composição da imagem importada."""
import io,sys,tempfile,unittest
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"engine"))
from scene_direction import story_scene,is_league_story
from story_art import classify,create_context_art,art_key
from external_prompt import prompt
from import_art import render_import
from poster import official_logo
from brand_assets import prepare,parse_logo

class ContextualCompositionTests(unittest.TestCase):
    def rube(self,issue=53):
        return {
            "episode_number":issue,"subject":"Rube Foster",
            "athlete":"Rube Foster",
            "title":"ELE NÃO ESPEROU PERMISSÃO PARA CONSTRUIR UMA LIGA.",
            "hook":"Antes das maiores mudanças do beisebol, Rube Foster organizou uma liga.",
            "art_direction":"ELE NÃO ESPEROU PERMISSÃO PARA CONSTRUIR UMA LIGA.",
            "narration":"Rube Foster e outros proprietários organizaram a Negro National League em 1920.",
            "art_revision":1,"unique_art_required":True,"content_type":"atleta"
        }

    def test_rube_never_has_ranked_cards(self):
        ep=self.rube()
        self.assertTrue(is_league_story(ep))
        self.assertEqual(classify(ep),"liga")
        scene=story_scene(ep)
        self.assertIn("Negro National League",scene)
        self.assertIn("1920",scene)
        self.assertIn("reunião",scene)
        self.assertIn("não reprodução documental",scene)
        image=create_context_art(ep)
        self.assertEqual(image.size,(1080,1180))
        newer=self.rube(issue=54)
        self.assertNotEqual(art_key(ep,0),art_key(newer,0))
        self.assertNotEqual(image.tobytes(),create_context_art(newer).tobytes())

    def test_external_prompt_has_actual_scene_not_just_title(self):
        ep=self.rube()
        result=prompt(ep)
        self.assertIn("CENA PRINCIPAL OBRIGATÓRIA",result)
        self.assertIn("Negro National League",result)
        self.assertIn("não reprodução documental",result)
        self.assertIn("NÃO um wireframe",result)
        self.assertIn("O ALLSTARS Studio adicionará DEPOIS",result)
        self.assertIn("Use referências visuais apenas como",result)
        self.assertNotIn("Preserve área livre para legendas na faixa central",result)
        self.assertIn("sem palavras",result)

    def test_uploaded_art_gets_studio_layout_and_profile(self):
        ep=self.rube()
        ep["art_source"]="uploaded"
        ep["art_image_fit"]="contain"
        ep["art_image_asset"]="external-r2-abcdef123456.jpg"
        ep["art_rights_confirmed"]=True
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            raw=folder/ep["art_image_asset"]
            Image.new("RGB",(760,1300),(60,135,125)).save(raw,"JPEG",quality=90)
            cover=folder/"capa.png"
            meta=render_import(raw,ep,cover)
            self.assertTrue(meta["layout_applied_by_studio"])
            self.assertTrue(meta["official_logo_used"])
            with Image.open(cover) as image:
                self.assertEqual(image.size,(1080,1920))
                self.assertNotEqual(image.getpixel((0,70)),(60,135,125))
                self.assertNotEqual(image.getpixel((540,1820)),(60,135,125))
            with Image.open(folder/"capa_perfil_3x4.png") as image:
                self.assertEqual(image.size,(1080,1440))

    def test_brand_fallback_stays_native_resolution(self):
        def offline(*args,**kwargs):raise OSError("offline")
        with tempfile.TemporaryDirectory() as d:
            result=prepare(Path(d)/"logo.png",opener=offline)
            self.assertEqual(result["source"],"repo_fallback_180px")
            with Image.open(Path(d)/"logo.png") as img:
                self.assertEqual(img.size,official_logo().size)

    def test_highres_official_logo_accepted_without_redrawing(self):
        image=Image.new("RGBA",(900,495),(100,70,40,255))
        out=io.BytesIO()
        image.save(out,format="PNG")
        data=out.getvalue()
        self.assertEqual(parse_logo(data).size,(900,495))

if __name__=="__main__":unittest.main()
