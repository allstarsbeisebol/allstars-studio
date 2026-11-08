#!/usr/bin/env python3
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from article_extract import extract_article

ARTICLE=" ".join("Roberto Clemente helped baseball history in Pittsburgh with his remarkable career and humanitarian work." for _ in range(18))
class ArticleExtractionTests(unittest.TestCase):
    def test_article_preferred_over_navigation(self):
        html=('<html><head><meta property="og:title" content="Clemente — Biography"></head>'
              '<body><nav><p>'+'Click navigation links '*65+'</p></nav>'
              '<main><article><h1>Roberto Clemente</h1><p>'+ARTICLE[:830]+'</p>'
              '<p>'+ARTICLE[830:]+'</p></article></main>'
              '<footer><p>'+'Footer junk '*100+'</p></footer></body></html>')
        d=extract_article(html,"https://baseballhall.org/hall-of-famers/clemente-roberto")
        self.assertEqual(d["title"],"Clemente — Biography")
        self.assertEqual(d["extraction_method"],"article")
        self.assertIn("Roberto Clemente",d["text"])
        self.assertNotIn("Click navigation links",d["text"])
        self.assertNotIn("Footer junk",d["text"])
        self.assertEqual(len(d["content_sha256"]),64)
        self.assertGreater(d["word_count"],75)
        self.assertEqual(d["verification_status"],"TEXTO EXTRAÍDO; FATOS NÃO VERIFICADOS")

    def test_jsonld_fallback_for_js_rendered_pages(self):
        article=" ".join("The athlete overcame difficult challenges while competing in professional baseball." for _ in range(23))
        obj={"@context":"https://schema.org","@type":"NewsArticle","headline":"A Story","articleBody":article}
        html='<html><head><title>Story</title><script type="application/ld+json">'+json.dumps(obj)+'</script></head><body><div id="app">Loading...</div></body></html>'
        d=extract_article(html,"https://example.com/story")
        self.assertEqual(d["extraction_method"],"schema.org/articleBody")
        self.assertIn("The athlete overcame",d["text"])

    def test_no_evidence_refuses_to_improvise(self):
        with self.assertRaisesRegex(ValueError,"texto de artigo suficiente"):
            extract_article("<html><title>Picture</title><body>Read more</body></html>","https://example.org/no-article")

    def test_html_size_is_bounded(self):
        with self.assertRaises(ValueError):
            extract_article("x"*1500001,"https://example.org")
if __name__=="__main__":
    unittest.main()
