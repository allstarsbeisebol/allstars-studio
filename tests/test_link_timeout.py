"""Testes determinísticos de leitura web lenta, sem acessar a internet."""
import io
import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
import from_link

ARTICLE=("Esta é uma matéria detalhada sobre um atleta de beisebol e sua carreira. " * 60).encode("utf-8")

class FakeHeaders:
    def get_content_type(self): return "text/html"
    def get(self,key,default=""): return default
    def get_content_charset(self): return "utf-8"

class FakeResponse:
    headers=FakeHeaders()
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,count):return ARTICLE[:count]

class FakeOpener:
    def __init__(self,fail_times=0):
        self.calls=0
        self.fail_times=fail_times
    def open(self,req,timeout):
        self.calls+=1
        if self.calls<=self.fail_times:raise socket.timeout("The read operation timed out")
        return FakeResponse()

class LinkTimeoutTests(unittest.TestCase):
    def run_fetch(self,fail_times):
        opener=FakeOpener(fail_times)
        with patch.object(from_link,"validate",side_effect=lambda url:url),\
             patch.object(from_link.urllib.request,"build_opener",return_value=opener),\
             patch.object(from_link.time,"sleep") as pause,\
             patch.object(from_link,"extract_article",return_value={
                 "title":"Biografia de atleta","text":"Um artigo público com informações verificáveis."
             }):
            if fail_times<3:
                result=from_link.read_page("https://example.org/story")
                self.assertEqual(result["submitted_url"],"https://example.org/story")
                self.assertEqual(result["title"],"Biografia de atleta")
                self.assertEqual(opener.calls,fail_times+1)
            else:
                with self.assertRaisesRegex(ValueError,"após 3 tentativas"):
                    from_link.read_page("https://example.org/story")
                self.assertEqual(opener.calls,3)
            self.assertEqual(pause.call_count,min(fail_times,2))

    def test_second_attempt_recovers(self):self.run_fetch(1)
    def test_third_attempt_recovers(self):self.run_fetch(2)
    def test_three_timeouts_report_clear_error(self):self.run_fetch(3)

if __name__=="__main__":unittest.main()
