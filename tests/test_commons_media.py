import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from commons_media import select_candidate, license_allowed, full_name_in

def page(title,license_name,author="Photographer",mime="image/jpeg"):
    return {"title":title,"imageinfo":[{
        "mime":mime,"width":1400,"height":1900,"size":950000,
        "thumburl":"https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/test-photo.jpg/1400px-test-photo.jpg",
        "descriptionurl":"https://commons.wikimedia.org/wiki/File:Test_photo.jpg",
        "extmetadata":{
            "LicenseShortName":{"value":license_name},
            "LicenseUrl":{"value":"https://creativecommons.org/licenses/by/4.0/"},
            "Artist":{"value":author}
        }
    }]}

class WikimediaMediaTests(unittest.TestCase):
    def test_permit_only_explicit_licenses_allowing_adaptation(self):
        for tag in ("CC0","CC BY 4.0","CC BY 3.0","Public domain"):
            self.assertTrue(license_allowed(tag),tag)
        for tag in ("CC BY-SA 4.0","CC BY-NC 4.0","CC BY-ND 4.0","Fair use","All rights reserved","Unknown"):
            self.assertFalse(license_allowed(tag),tag)
    def test_exact_athlete_name_and_author_required(self):
        pages={
            "10":page("File:Roberto Clemente in Pittsburgh 1967.jpg","CC BY 4.0"),
            "11":page("File:Roberto another baseball athlete.jpg","CC BY 4.0"),
        }
        c=select_candidate(pages,"Roberto Clemente")
        self.assertEqual(c["license"],"CC BY 4.0")
        self.assertIn("Roberto Clemente",c["title"])
        self.assertEqual(c["source"],"Wikimedia Commons")
        self.assertEqual(c["author"],"Photographer")
    def test_reject_name_mismatch_and_no_author(self):
        self.assertIsNone(select_candidate({"1":page("File:Jackie Robinson pitching.jpg","CC BY 4.0")},"Jim Abbott"))
        self.assertIsNone(select_candidate({"1":page("File:Jim Abbott baseball.jpg","CC BY 4.0",author="")},"Jim Abbott"))
        self.assertFalse(full_name_in("File:Jim baseball.jpg","Jim Abbott"))
    def test_reject_sharealike_and_unlicensed(self):
        self.assertIsNone(select_candidate({"1":page("File:Curt Flood baseball.jpg","CC BY-SA 4.0")},"Curt Flood"))
        self.assertIsNone(select_candidate({"1":page("File:Curt Flood baseball.jpg","No license")},"Curt Flood"))
if __name__=="__main__":unittest.main()
