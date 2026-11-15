"""Comportamento seguro para HTTP 429 sem consumo de API real."""
import json
import sys
import unittest
import urllib.error
from email.message import Message
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"engine"))
from topic_generate import create_topic,quota_retry_seconds


class QuotaTests(unittest.TestCase):
    def test_retry_after_short_interval(self):
        headers=Message()
        headers["Retry-After"]="2"
        self.assertEqual(quota_retry_seconds(headers),2)

    def test_daily_or_unknown_limit_never_retried(self):
        for value in ("", "500", "0", "not-a-number", "Wed, 15 Nov 2026 22:00:00 GMT"):
            headers=Message()
            if value:
                headers["Retry-After"]=value
            self.assertIsNone(quota_retry_seconds(headers))

    def test_429_without_delay_fails_once_without_fake_sources(self):
        headers=Message()
        error=urllib.error.HTTPError(
            "https://generativelanguage.googleapis.com",429,"Too Many Requests",
            headers,None)
        with patch.dict("os.environ",{"GEMINI_API_KEY":"test-only-key","GEMINI_MODEL":"gemini-test"}):
            with patch("topic_generate.urllib.request.urlopen",side_effect=error) as fetch:
                with self.assertRaisesRegex(ValueError,"HTTP 429") as ctx:
                    create_topic({"content_type":"tema","subject":"Evolução das jerseys no baseball"})
                self.assertEqual(fetch.call_count,1)
                self.assertIn("O pedido foi preservado",str(ctx.exception))

    def test_429_with_short_retry_after_attempts_at_most_twice(self):
        headers=Message()
        headers["Retry-After"]="1"
        error=urllib.error.HTTPError(
            "https://generativelanguage.googleapis.com",429,"Too Many Requests",
            headers,None)
        with patch.dict("os.environ",{"GEMINI_API_KEY":"test-only-key","GEMINI_MODEL":"gemini-test"}):
            with patch("topic_generate.urllib.request.urlopen",side_effect=error) as fetch:
                with patch("topic_generate.time.sleep") as sleeper:
                    with self.assertRaisesRegex(ValueError,"HTTP 429"):
                        create_topic({"content_type":"tema","subject":"Evolução das jerseys no baseball"})
                    self.assertEqual(fetch.call_count,2)
                    sleeper.assert_called_once_with(1)


if __name__=="__main__":
    unittest.main()
