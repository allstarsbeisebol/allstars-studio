"""Testes estáticos de integração visual: não substituem QA com navegador."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "public/index.html").read_text(encoding="utf-8")
CSS = (ROOT / "public/studio-motion.css").read_text(encoding="utf-8")

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stylesheets = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.stylesheets.append(attrs.get("href"))

class VisualFoundationTests(unittest.TestCase):
    def test_stylesheet_loaded_from_public(self):
        parser = Links()
        parser.feed(HTML)
        self.assertIn("./studio-motion.css", parser.stylesheets)
        self.assertTrue((ROOT / "public/studio-motion.css").is_file())

    def test_brand_tokens(self):
        for color in ("#1a3566", "#315fac", "#ce233e", "#f0c040"):
            self.assertIn(color, CSS.lower())

    def test_keyboard_and_reduced_motion(self):
        self.assertIn(":focus-visible", CSS)
        self.assertIn("outline:", CSS)
        self.assertIn("prefers-reduced-motion: reduce", CSS)
        self.assertIn("transition: none !important", CSS)
        self.assertIn("animation: none !important", CSS)

    def test_no_external_runtime_dependencies(self):
        self.assertNotIn("@import", CSS)
        self.assertNotIn("url(", CSS)
        self.assertNotIn("javascript:", CSS)

    def test_wizard_not_removed(self):
        for element_id in ("wizard-steps", "wizard-content-next",
                           "wizard-references-back", "art-approve",
                           "home-continue", "downloads"):
            self.assertIn('id="' + element_id + '"', HTML)

if __name__ == "__main__":
    unittest.main()
