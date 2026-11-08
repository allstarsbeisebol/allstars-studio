"""Teste do banco de imagens anime: aprovação por atleta, não mistura personagens."""
import json,tempfile,sys,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
import anime_assets

class ApprovedAnimeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.old_folder=anime_assets.FOLDER
        anime_assets.FOLDER=Path(self.temp.name)
    def tearDown(self):
        anime_assets.FOLDER=self.old_folder
        self.temp.cleanup()
    def asset(self, name="Jim Abbott", approved=True):
        image=Image.new("RGB",(540,960),(20,50,100))
        image.save(anime_assets.FOLDER/"jim-abbott.webp","WEBP")
        (anime_assets.FOLDER/"jim-abbott.json").write_text(json.dumps({
            "athlete":name,"file":"jim-abbott.webp","approved":approved,
            "visual_type":"original_anime_illustration",
            "source_note":"Arte aprovada para projeto","rights_basis":"Original autorizado"
        }),encoding="utf-8")
    def test_approved_image_selected_only_for_matching_athlete(self):
        self.asset()
        found=anime_assets.cover_from_approved_asset({"athlete":"Jim Abbott"})
        self.assertIsNotNone(found)
        self.assertEqual(found[0].size,(1080,1920))
        self.assertIsNotNone(anime_assets.hero_from_approved_asset({"athlete":"Jim Abbott"}))
        self.assertIsNone(anime_assets.cover_from_approved_asset({"athlete":"Roberto Clemente"}))
    def test_unapproved_image_is_rejected(self):
        self.asset(approved=False)
        self.assertIsNone(anime_assets.cover_from_approved_asset({"athlete":"Jim Abbott"}))
    def test_mismatched_metadata_is_rejected(self):
        self.asset(name="Roberto Clemente")
        self.assertIsNone(anime_assets.cover_from_approved_asset({"athlete":"Jim Abbott"}))
    def test_wrong_shape_is_rejected(self):
        self.asset()
        Image.new("RGB",(960,540)).save(anime_assets.FOLDER/"jim-abbott.webp","WEBP")
        self.assertIsNone(anime_assets.cover_from_approved_asset({"athlete":"Jim Abbott"}))

if __name__=="__main__":unittest.main()
