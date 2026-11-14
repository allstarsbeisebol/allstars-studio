"""Smoke visual real em Chromium, sem login, API ou dados de produção."""
import http.server
import socketserver
import threading
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

PUBLIC = Path(__file__).resolve().parents[1] / "public"

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

class BrowserSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(PUBLIC), **kwargs)
        cls.server = socketserver.TCPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_address[1]}/"
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def test_viewports_and_navigation(self):
        for width, height in [(320, 740), (390, 844), (535, 780), (1280, 900)]:
            with self.subTest(width=width):
                page = self.browser.new_page(viewport={"width": width, "height": height},
                                             reduced_motion="reduce")
                try:
                    page.goto(self.url, wait_until="domcontentloaded")
                    page.locator(".hero h1").wait_for(state="visible")
                    self.assertEqual(page.locator(".hero h1").count(), 1)
                    dimensions = page.evaluate("""() => ({
                        viewport: document.documentElement.clientWidth,
                        scroll: document.documentElement.scrollWidth,
                        hero: document.querySelector('.hero h1').getBoundingClientRect().right
                    })""")
                    self.assertLessEqual(dimensions["scroll"], dimensions["viewport"] + 1,
                                         f"Horizontal overflow at {width}px: {dimensions}")
                    self.assertLessEqual(dimensions["hero"], width + 1)
                    if width <= 680:
                        toggle = page.locator("#mobile-menu-toggle")
                        self.assertTrue(toggle.is_visible())
                        toggle.click()
                        self.assertEqual(toggle.get_attribute("aria-expanded"), "true")
                        page.keyboard.press("Escape")
                        self.assertEqual(toggle.get_attribute("aria-expanded"), "false")
                    else:
                        self.assertFalse(page.locator("#mobile-menu-toggle").is_visible())
                    page.screenshot(path=f"/tmp/allstars-mobile-{width}.png", full_page=False)
                finally:
                    page.close()

if __name__ == "__main__":
    unittest.main()
