"""Testes offline da memória visual e da sincronização segura."""
import json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
import visual_sync
from external_prompt import prompt

class VisualSyncTests(unittest.TestCase):
    def episode(self):
        return {"episode_number":53,"subject":"Jim Abbott","title":"Uma noite histórica",
                "hook":"Uma história de beisebol","art_direction":"Arremesso em campo",
                "art_revision":2,"art_source":"uploaded","art_rights_confirmed":True}

    def test_missing_keys_do_not_interrupt_video(self):
        with patch.dict(os.environ,{},clear=True):
            self.assertFalse(visual_sync.enabled())
            self.assertEqual(visual_sync.archive(self.episode(),"preview")["status"],"skipped_not_configured")

    def test_project_mismatch_is_blocked(self):
        with patch.dict(os.environ,{
          "SUPABASE_URL":"https://wrong.supabase.co",
          "SUPABASE_SERVICE_ROLE_KEY":"not-a-real-key"
        }):
            self.assertFalse(visual_sync.enabled())

    def test_memory_empty_offline(self):
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{},clear=True):
            path=Path(d)/"memory.json"
            self.assertEqual(visual_sync.memory(path),[])
            self.assertEqual(json.loads(path.read_text()),[])

    def test_approved_memory_included_without_replacing_original_art_direction(self):
        with tempfile.TemporaryDirectory() as d:
            old=os.getcwd()
            try:
                os.chdir(d)
                Path("output").mkdir()
                Path("output/style_memory.json").write_text(json.dumps([
                  {"preference":"prefer","summary":"Destacar expressões faciais e iluminação."},
                  {"preference":"avoid","summary":"Não repetir imagens de outros episódios."}
                ],ensure_ascii=False),encoding="utf-8")
                value=prompt(self.episode())
                self.assertIn("PRIORIZE: Destacar expressões",value)
                self.assertIn("EVITE: Não repetir",value)
                self.assertIn("CENA E CONTEXTO ESPECÍFICOS: Arremesso em campo",value)
            finally:
                os.chdir(old)

    def test_cover_is_compressed_for_private_storage(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"capa.png"
            Image.new("RGB",(1080,1920),(20,85,150)).save(source)
            output,w,h=visual_sync.cover_bytes(source)
            self.assertLess(len(output),1900000)
            self.assertEqual((w,h),(1080,1920))
            self.assertTrue(output.startswith(b"\xff\xd8"))

    def test_upload_variant_is_distinct_from_generated_art(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"capa.png"
            Image.new("RGB",(1080,1920),(20,85,150)).save(path)
            old_url=visual_sync.URL
            with patch.dict(os.environ,{
                "SUPABASE_URL":old_url,
                "SUPABASE_SERVICE_ROLE_KEY":"only-for-mocked-tests"
            }):
                calls=[]
                def mock_rest(table,query="",body=None,method=None,prefer=None):
                    calls.append((table,query,body,method))
                    if table=="allstars_episodes":return [{"id":"test-episode-id"}]
                    if table=="allstars_visual_assets" and body is None:return []
                    if table=="allstars_visual_prompts":return [{"id":"test-prompt-id"}]
                    if table=="allstars_visual_assets":return [{"id":"test-asset-id"}]
                    raise ValueError("Unexpected table")
                with patch.object(visual_sync,"rest",side_effect=mock_rest),patch.object(visual_sync,"api",return_value={}):
                    result=visual_sync.archive(self.episode(),"preview",root=Path(d))
                self.assertEqual(result["status"],"archived")
                final=next(data[2][0] for data in calls if data[0]=="allstars_visual_assets" and data[2])
                self.assertEqual(final["source_kind"],"edited_variant")
                self.assertTrue(final["rights_confirmed"])
                self.assertEqual(final["approval_status"],"review")
                self.assertEqual(final["metadata"]["base_source"],"uploaded_original")

if __name__=="__main__":unittest.main()
