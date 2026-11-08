"""Testes de arte editorial inédita sem depender de APIs externas."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"engine"))
from story_art import create_context_art,art_key,art_metadata,classify
from anime_assets import find_approved_anime

class OriginalArtTests(unittest.TestCase):
    def episode(self,number):
        return {"id":"pesquisa-real","episode_number":number,"athlete":"Jogador fictício de teste",
                "subject":"No-hitter histórico de 1993","title":"Um jogo sem rebatidas",
                "hook":"Como aconteceu o no-hitter da temporada de 1993?",
                "narration":"Em 1993 houve um no-hitter documentado.",
                "screens":["Arremesso decisivo","Números da partida"],
                "art_direction":"Cena de arremesso com zona de strike e ano 1993",
                "content_type":"atleta","unique_art_required":True}

    def test_image_is_new_between_runs(self):
        a,b=self.episode(101),self.episode(102)
        self.assertNotEqual(art_key(a,0),art_key(b,0))
        self.assertNotEqual(art_key(a,0),art_key(a,1))
        ia,ib=create_context_art(a,0),create_context_art(b,0)
        self.assertEqual(ia.size,(1080,1180))
        self.assertNotEqual(ia.tobytes(),ib.tobytes())
        self.assertEqual(art_metadata(a)["visual_type"],"original_contextual_vector_art")

    def test_no_reuse_approved_cover(self):
        a=self.episode(101)
        a["athlete"]="Jim Abbott"
        a["title"]="1993: O NO-HITTER DE JIM ABBOTT"
        self.assertIsNone(find_approved_anime(a))

    def test_topic_semantics_change_composition(self):
        a=self.episode(101)
        b=dict(a,subject="História do contrato de jogadores",title="Contrato e direitos",narration="O contrato mudou")
        self.assertEqual(classify(a),"arremesso")
        self.assertEqual(classify(b),"contrato")
        self.assertNotEqual(create_context_art(a).tobytes(),create_context_art(b).tobytes())

if __name__=="__main__":unittest.main()
