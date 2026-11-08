"""Smoke tests for the exact Jim Abbott illustration approved in the repository."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from anime_assets import find_approved_anime,cover_from_approved_asset,hero_from_approved_asset

class JimAbbottApprovedAsset(unittest.TestCase):
    def episode(self,title="JIM ABBOTT: O NO-HITTER DE 1993"):
        return {"athlete":"Jim Abbott","title":title,
                "narration":"Em 1993 Jim Abbott conseguiu um no-hitter histórico.",
                "screens":["UMA NOITE INESQUECÍVEL"]}
    def test_approved_art_is_real_repo_asset(self):
        result=find_approved_anime(self.episode())
        self.assertIsNotNone(result)
        image,info=result
        self.assertEqual(info["source_git_blob_sha"],"be76e4af48d2227d5fe16915566d6b1bf3f2e48e")
        self.assertEqual(image.size,(941,1672))
        self.assertTrue(info["approved"])
        self.assertIn("Jim Abbott",info["source_note"])
    def test_anime_cropped_for_video_has_transparency_and_no_footer(self):
        img,_=hero_from_approved_asset(self.episode())
        self.assertEqual(img.size,(1080,1135))
        self.assertEqual(img.getpixel((500,1120))[3],0)
        self.assertGreater(img.getpixel((500,350))[3],0)
    def test_approved_poster_has_9_by_16_cover(self):
        cover,_=cover_from_approved_asset(self.episode())
        self.assertEqual(cover.size,(1080,1920))
    def test_do_not_steal_image_for_another_athlete_or_unrelated_story(self):
        self.assertIsNone(find_approved_anime({
            "athlete":"Roberto Clemente","title":"No-hitter 1993"}))
        self.assertIsNone(find_approved_anime({
            "athlete":"Jim Abbott","title":"O início de uma carreira",
            "narration":"Jim Abbott foi jogador de beisebol."}))
if __name__=="__main__":unittest.main()
