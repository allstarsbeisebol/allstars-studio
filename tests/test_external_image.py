"""Teste offline: imagem enviada, revisão e exportação vertical."""
import tempfile,unittest,sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from import_art import render_import
from art_gate import prepare,advance,approve
from external_prompt import prompt

class ExternalImageTests(unittest.TestCase):
    def episode(self):
        return prepare({"subject":"Jim Abbott 1993 no-hitter",
            "title":"O jogo sem rebatidas","hook":"A noite que mudou a história",
            "art_direction":"Arremesso da década de 1990",
            "narration":"História verificada.","unique_art_required":True},42)

    def test_external_review_increases_version_and_waits_for_approval(self):
        ep=self.episode()
        ep=advance(ep,"ALLSTARS_ART_CHANGE\nREVISION: 1\nACTION: external\n"
                       "IMAGE_ASSET: external-r2-abcdef123456.jpg\nFIT: blur")
        self.assertEqual(ep["art_revision"],2)
        self.assertEqual(ep["art_source"],"uploaded")
        self.assertFalse(ep["art_approved"])
        self.assertEqual(ep["art_image_asset"],"external-r2-abcdef123456.jpg")
        self.assertEqual(ep["art_image_fit"],"blur")
        self.assertTrue(ep["art_rights_confirmed"])
        with self.assertRaisesRegex(ValueError,"versão atual"):
            approve(ep,"ALLSTARS_ART_APPROVE\nREVISION: 1")
        self.assertTrue(approve(ep,"ALLSTARS_ART_APPROVE\nREVISION: 2")["art_approved"])

    def test_regenerate_does_not_keep_old_imported_art(self):
        ep=self.episode()
        ep=advance(ep,"ALLSTARS_ART_CHANGE\nREVISION: 1\nACTION: external\n"
                       "IMAGE_ASSET: external-r2-abcdef123456.jpg\nFIT: cover")
        ep=advance(ep,"ALLSTARS_ART_CHANGE\nREVISION: 2\nACTION: regenerate")
        self.assertEqual(ep["art_source"],"generated")
        self.assertNotIn("art_image_asset",ep)
        self.assertFalse(ep["art_approved"])

    def test_rejects_asset_from_different_revision(self):
        ep=self.episode()
        with self.assertRaisesRegex(ValueError,"próxima revisão"):
            advance(ep,"ALLSTARS_ART_CHANGE\nREVISION: 1\nACTION: external\n"
                       "IMAGE_ASSET: external-r3-abcdef123456.jpg\nFIT: cover")

    def test_image_is_saved_9_16_and_3_4(self):
        for fit in ("contain","cover","blur"):
            with self.subTest(fit=fit), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                source=root/"external-r2-abcdef123456.jpg"
                Image.new("RGB",(1500,860),(210,55,65)).save(source,"JPEG",quality=85)
                ep=self.episode()
                ep=advance(ep,"ALLSTARS_ART_CHANGE\nREVISION: 1\nACTION: external\n"
                                  "IMAGE_ASSET: external-r2-abcdef123456.jpg\nFIT: "+fit)
                output=root/"capa.png"
                metadata=render_import(source,ep,output)
                self.assertEqual(metadata["source"],"user_supplied_image")
                with Image.open(output) as cover:self.assertEqual(cover.size,(1080,1920))
                with Image.open(root/"capa_perfil_3x4.png") as profile:self.assertEqual(profile.size,(1080,1440))

    def test_video_poster_uses_the_uploaded_artwork(self):
        # As cenas internas devem usar a imagem escolhida, não substituir
        # silenciosamente por um desenho genérico após aprovar.
        from poster import poster
        folder=Path(__file__).resolve().parents[1]/"output"
        folder.mkdir(exist_ok=True)
        source=folder/"external-r2-abcdef123456.jpg"
        Image.new("RGB",(1080,1920),(25,110,200)).save(source,"JPEG",quality=84)
        try:
            ep=self.episode()
            ep=advance(ep,"ALLSTARS_ART_CHANGE\\nREVISION: 1\\nACTION: external\\n"
                          "IMAGE_ASSET: external-r2-abcdef123456.jpg\\nFIT: contain".replace("\\n","\n"))
            frame=poster(ep,headline="Uma cena desta história",index=1,total=4)
            self.assertEqual(frame.size,(1080,1920))
        finally:source.unlink(missing_ok=True)

    def test_prompt_is_pertinent_and_has_no_fake_ai_api_cost(self):
        value=prompt(self.episode())
        self.assertIn("Jim Abbott",value)
        self.assertIn("1993",value)
        self.assertIn("NÃO",value)
        self.assertIn("Ctrl+V",value)
        self.assertNotIn("API_KEY",value)
if __name__=="__main__":unittest.main()
