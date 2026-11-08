"""Valida revisão visual antes da geração de vídeo, sem usar APIs pagas."""
import base64,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from art_gate import prepare,advance,approve
from story_art import art_key

class ArtGateTests(unittest.TestCase):
    def episode(self):
        return prepare({"id":"test-ep","subject":"O home run de 1993",
                        "title":"Uma história de beisebol","art_direction":"Bola no estádio",
                        "unique_art_required":True,"narration":"Uma história documentada."},88)

    def test_does_not_approve_before_editor(self):
        ep=self.episode()
        self.assertEqual(ep["art_revision"],1)
        self.assertFalse(ep["art_approved"])
        self.assertEqual(ep["episode_number"],88)

    def test_regeneration_creates_another_original_art(self):
        ep=self.episode();before=art_key(ep,0)
        ep=advance(ep,"ALLSTARS_ART_CHANGE\nREVISION: 1\nACTION: regenerate\nFEEDBACK_BASE64: ")
        self.assertEqual(ep["art_revision"],2)
        self.assertNotEqual(before,art_key(ep,0))
        self.assertFalse(ep["art_approved"])

    def test_editor_revision_changes_direction(self):
        ep=self.episode()
        note="Destacar a bola com vermelho e desenhar o arremesso."
        encoded=base64.b64encode(note.encode("utf-8")).decode("ascii")
        ep=advance(ep,"ALLSTARS_ART_CHANGE\nREVISION: 1\nACTION: revise\nFEEDBACK_BASE64: "+encoded)
        self.assertIn(note,ep["art_direction"])
        self.assertEqual(ep["art_revision"],2)
        self.assertEqual(ep["art_feedback"],note)

    def test_only_current_revision_can_be_approved(self):
        ep=self.episode()
        with self.assertRaisesRegex(ValueError,"versão atual"):
            approve(ep,"ALLSTARS_ART_APPROVE\nREVISION: 2")
        out=approve(ep,"ALLSTARS_ART_APPROVE\nREVISION: 1")
        self.assertTrue(out["art_approved"])
        self.assertEqual(out["approved_art_revision"],1)

    def test_unknown_action_rejected(self):
        ep=self.episode()
        with self.assertRaises(ValueError):
            advance(ep,"ALLSTARS_ART_CHANGE\nREVISION: 1\nACTION: delete")
if __name__=="__main__":unittest.main()
