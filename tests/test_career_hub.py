import os
import re
import unittest
import zipfile
from bs4 import BeautifulSoup

class TestCareerHub(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.index_path = os.path.join(self.root_dir, "index.html")
        self.style_path = os.path.join(self.root_dir, "style.css")
        self.hub_js_path = os.path.join(self.root_dir, "hub.js")
        self.zip_path = os.path.join(self.root_dir, "download", "resume-template-starter.zip")

    def test_01_hub_structure_and_anchors(self):
        self.assertTrue(os.path.exists(self.index_path), "index.html must exist")
        with open(self.index_path, "r", encoding="utf-8") as f:
            content = f.read()

        soup = BeautifulSoup(content, "html.parser")
        required_ids = ["hero", "prompts", "workflows", "resume", "download"]
        for req_id in required_ids:
            elem = soup.find(id=req_id)
            self.assertIsNotNone(elem, f"Missing section #{req_id} in index.html")

    def test_02_zero_emojis_invariant(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            content = f.read()

        emoji_pattern = re.compile(
            "[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\U0001f300-\U0001f9ff]",
            flags=re.UNICODE
        )
        matches = emoji_pattern.findall(content)
        self.assertEqual(len(matches), 0, f"Found prohibited emojis in index.html: {set(matches)}")

    def test_03_prompt_library_cards(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, "html.parser")
        prompt_cards = soup.select(".prompt-card")
        self.assertGreaterEqual(len(prompt_cards), 5, f"Expected at least 5 prompt cards, found {len(prompt_cards)}")

    def test_04_print_isolation(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, "html.parser")
        resume_paper = soup.find(id="resume-paper")
        self.assertIsNotNone(resume_paper, "Missing #resume-paper container")

        top_nav = soup.find(id="top-nav")
        self.assertIsNotNone(top_nav, "Missing #top-nav element")
        classes = top_nav.get("class", [])
        self.assertIn("no-print", classes, "Top nav must have 'no-print' class")

    def test_05_skills_directory(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, "html.parser")
        skill_items = soup.select(".skill-item")
        self.assertGreaterEqual(len(skill_items), 20, f"Expected at least 20 skills listed, found {len(skill_items)}")

    def test_06_starter_kit_zip(self):
        if os.path.exists(self.zip_path):
            self.assertGreater(os.path.getsize(self.zip_path), 1000, "Starter zip is too small or corrupt")
            with zipfile.ZipFile(self.zip_path, 'r') as z:
                names = z.namelist()
                self.assertTrue(any("profile.example.json" in n for n in names), "Missing profile.example.json in ZIP")
                self.assertTrue(any("cover_letter_prompt.txt" in n for n in names), "Missing prompt files in ZIP")

    def test_07_hub_js_syntax_and_invariants(self):
        self.assertTrue(os.path.exists(self.hub_js_path), "hub.js must exist")
        with open(self.hub_js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # Check required handlers exist
        self.assertIn("function copyPrompt", js_content)
        self.assertIn("function switchPersona", js_content)
        self.assertIn("function toggleAtsMode", js_content)

        # Zero emojis invariant in JS
        emoji_pattern = re.compile(
            "[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\U0001f300-\U0001f9ff]",
            flags=re.UNICODE
        )
        matches = emoji_pattern.findall(js_content)
        self.assertEqual(len(matches), 0, f"Prohibited emojis found in hub.js: {set(matches)}")

    def test_08_resume_html_separation(self):
        resume_path = os.path.join(self.root_dir, "resume.html")
        self.assertTrue(os.path.exists(resume_path), "resume.html must exist as standalone resume")
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_content = f.read()

        self.assertIn('id="resumeContent"', resume_content, "resume.html must contain #resumeContent")

        # Zero emojis in resume.html
        emoji_pattern = re.compile(
            "[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\U0001f300-\U0001f9ff]",
            flags=re.UNICODE
        )
        matches = emoji_pattern.findall(resume_content)
        self.assertEqual(len(matches), 0, f"Found prohibited emojis in resume.html: {set(matches)}")

        # index.html should not duplicate resumeContent
        with open(self.index_path, "r", encoding="utf-8") as f:
            index_content = f.read()
        self.assertNotIn('id="resumeContent"', index_content, "index.html must not inline #resumeContent")
        self.assertIn('id="resume-paper"', index_content, "index.html must maintain #resume-paper preview container")
        self.assertIn('id="resumeFrame"', index_content, "index.html must embed #resumeFrame preview")

if __name__ == "__main__":
    unittest.main()
