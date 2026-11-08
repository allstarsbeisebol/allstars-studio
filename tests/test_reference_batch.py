"""Valida várias fontes sem impor limite de cinco caixas."""
import base64,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from content_request import parse

class ReferenceTests(unittest.TestCase):
    def test_many_urls_are_accepted_and_deduplicated(self):
        links=["https://example.com/article-"+str(i) for i in range(27)]
        body="MODO: link\nTIPO: tema\nASSUNTO: História da MLB\n"+"\n".join("LINK: "+x for x in links+[links[0]])
        parsed=parse(body)
        self.assertEqual(parsed["urls"],links)
    def test_limit_is_total_size_for_safety(self):
        links=["https://example.com/"+str(i)+"/"+("a"*900) for i in range(30)]
        with self.assertRaisesRegex(ValueError,"24 mil"):
            parse("\n".join("LINK: "+x for x in links))
if __name__=="__main__":unittest.main()
