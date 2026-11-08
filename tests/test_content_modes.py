"""Tipo de conteúdo, assunto opcional e verificação editorial não individual."""
import sys,unittest,base64
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from content_request import parse
from editorial_guard import verify_reference

class ContentModeTests(unittest.TestCase):
    def test_original_automatic_still_works(self):
        req=parse("MODO: auto\n\nGerar próxima história")
        self.assertEqual(req["content_type"],"auto")
        self.assertEqual(req["subject"],"")
    def test_topic_without_link(self):
        req=parse("MODO: auto\nTIPO: tema\nASSUNTO: História do Hall da Fama\n")
        self.assertEqual((req["mode"],req["content_type"]),("auto","tema"))
        self.assertEqual(req["subject"],"História do Hall da Fama")
    def test_explainer_collective_article(self):
        req=parse("MODO: link\nTIPO: explicativo\nASSUNTO: Como funciona o Hall da Fama\nLINK: https://www.olympics.com/es/noticias/salon-fama-beisbol-mlb-todos-miembros")
        self.assertEqual(req["content_type"],"explicativo")
        self.assertTrue(req["url"].startswith("https://"))
    def test_bad_type_and_line_rejected(self):
        with self.assertRaisesRegex(ValueError,"Tipo"):parse("TIPO: absurdo")
        with self.assertRaisesRegex(ValueError,"assunto|Assunto"):parse("TIPO: lista")
    def test_multiple_links_and_pasted_text(self):
        payload=base64.b64encode("Texto sobre beisebol público com acentos e fontes.".encode()).decode()
        req=parse("MODO: link\\nTIPO: tema\\nASSUNTO: Regras do jogo\\nLINK: https://www.mlb.com/test\\nLINK: https://www.instagram.com/p/demo/\\nTEXTO_BASE64: "+payload)
        self.assertEqual(len(req["urls"]),2)
        self.assertIn("acentos",req["reference_text"])
        self.assertEqual(req["url"],"https://www.mlb.com/test")
    def test_invalid_sources(self):
        with self.assertRaises(ValueError):
            parse("TIPO: tema\\nLINK: http://insecure.com")
        with self.assertRaises(ValueError):
            parse("TIPO: tema\\nTEXTO_BASE64: invalid!")
    def test_years_checked_without_single_player(self):
        article={"title":"Hall da Fama","text":"A exposição abriu em 1939. O Hall da Fama tem extensa história."}
        ep={"athlete":"Hall da Fama","title":"O Hall desde 1939","narration":"O Hall tem história desde 1939.","screens":["EXPLICANDO O HALL"],"evidence_paragraphs":["P01"]}
        out=verify_reference(article,ep,require_athlete=False)
        self.assertIsNone(out["athlete_mentioned_in_source"])
        with self.assertRaisesRegex(ValueError,"1995"):
            ep["narration"]="O Hall começou em 1995"
            verify_reference(article,ep,require_athlete=False)
if __name__=="__main__":unittest.main()
