"""Pesquisa complementar a partir de URLs bloqueadas, sem trocar o assunto."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from source_adaptation import describe_reference,adapt_with_research

class AdaptationTests(unittest.TestCase):
    def test_user_topic_has_priority(self):
        text,origin=describe_reference({"subject":"O arremesso de Jim Abbott",
                                         "urls":["https://instagram.com/p/AaBbCcDdEE/"]})
        self.assertEqual(text,"O arremesso de Jim Abbott")
        self.assertEqual(origin,"subject")

    def test_descriptive_url_is_search_hint(self):
        topic,origin=describe_reference({"subject":"","reference_text":"",
                                         "urls":["https://example.org/news/como-roberto-clemente-mudou-o-beisebol"]})
        self.assertIn("roberto clemente",topic)
        self.assertEqual(origin,"url_slug_hint")

    def test_opaque_social_id_not_made_up_as_story(self):
        topic,origin=describe_reference({"subject":"","reference_text":"",
                                         "urls":["https://instagram.com/p/AB12CdEfgHijkl/"]})
        self.assertEqual(topic,"")
        self.assertEqual(origin,"insufficient_context")
        with self.assertRaisesRegex(ValueError,"não revelam o assunto"):
            adapt_with_research({"subject":"","urls":["https://instagram.com/p/AB12CdEfgHijkl/"],"reference_text":""},[])

    def test_short_explanation_serves_as_hint_not_verified_fact(self):
        topic,origin=describe_reference({"subject":"","reference_text":"Jim Abbott lançou um jogo sem rebatidas.","urls":[]})
        self.assertTrue(topic.startswith("Jim Abbott"))
        self.assertEqual(origin,"user_text_hint")

    def test_fallback_preserves_original_urls_separately(self):
        original="https://instagram.com/p/AB12CdEfgHijkl/"
        grounded="https://baseballhall.org/hall-of-famers/abbott-jim"
        mock={
            "subject":"Jim Abbott","title":"História documentada","sources":[grounded],
            "hook":"O que tornou aquela partida inesquecível?","art_direction":"Stadium"
        }
        with patch("topic_generate.create_topic",return_value=mock):
            ep=adapt_with_research({"subject":"Jim Abbott","urls":[original],"reference_text":"","content_type":"atleta"},
                                   [{"url":original,"reason":"Rede social bloqueada"}])
        self.assertEqual(ep["sources"],[original,grounded])
        self.assertEqual(ep["original_reference_urls"],[original])
        self.assertFalse(ep["source_metadata"]["original_urls_verified"])
        self.assertEqual(ep["source_metadata"]["complementary_source_urls"],[grounded])
        self.assertEqual(ep["source_mode"],"allstars_complementary_research")
if __name__=="__main__":unittest.main()
