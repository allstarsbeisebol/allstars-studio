import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from editorial_guard import verify_reference

class EditorialGuardTests(unittest.TestCase):
    def test_athlete_and_year_supported_by_article(self):
        article={"title":"Curt Flood — A luta", "text":"Em 1969, Curt Flood desafiou as regras do beisebol. Em 1972 houve uma decisão na justiça."}
        ep={"athlete":"Curt Flood","title":"A luta de 1969","narration":"Em 1972 o processo terminou.","screens":["1969 · UM ATO DE CORAGEM"],"evidence_paragraphs":["P01"]}
        result=verify_reference(article,ep)
        self.assertEqual(result["unsupported_years"],[])
        self.assertFalse(result["verified_independently"])
    def test_refuse_unsupported_historical_year(self):
        article={"title":"Curt Flood","text":"Curt Flood enfrentou os donos dos clubes em 1969."}
        ep={"athlete":"Curt Flood","title":"1979 · A VITÓRIA","narration":"Curt Flood lutou em 1969","screens":[]}
        with self.assertRaisesRegex(ValueError,"1979"):
            verify_reference(article,ep)
    def test_refuse_wrong_athlete(self):
        article={"title":"Larry Doby","text":"Larry Doby entrou para a história dos times de beisebol."}
        ep={"athlete":"Roberto Clemente","narration":"Roberto Clemente inspirou gerações.","screens":[]}
        with self.assertRaisesRegex(ValueError,"não foi encontrado"):
            verify_reference(article,ep)
    def test_unreferenced_story_is_marked_for_review(self):
        article={"title":"Larry Doby","text":"Larry Doby foi um pioneiro importante."}
        ep={"athlete":"Larry Doby","title":"UM PIONEIRO","narration":"Larry Doby abriu portas.","screens":[]}
        output=verify_reference(article,ep)
        self.assertIn("REFERÊNCIAS INSUFICIENTES",output["status"])
if __name__=="__main__":unittest.main()
