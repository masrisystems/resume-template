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
        required_ids = [
            "hero",
            "daily-workflow",
            "brief-showcase",
            "prompts",
            "cover-letters",
            "engine",
            "workflows",
            "resume",
            "download"
        ]
        for req_id in required_ids:
            elem = soup.find(id=req_id)
            self.assertIsNotNone(elem, f"Missing section #{req_id} in index.html")

        # Verify all nav links point to existing IDs
        nav = soup.find(id="top-nav")
        self.assertIsNotNone(nav, "Missing #top-nav")
        for a in nav.select(".nav-links a"):
            href = a.get("href", "")
            if href.startswith("#"):
                anchor_id = href.lstrip("#")
                self.assertIsNotNone(soup.find(id=anchor_id), f"Nav link {href} points to non-existent ID #{anchor_id}")

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
        self.assertGreaterEqual(len(prompt_cards), 7, f"Expected at least 7 prompt cards, found {len(prompt_cards)}")

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
        self.assertIn("function copyEngineCommand", js_content)
        self.assertIn("function switchBrief", js_content)
        self.assertIn("function switchCoverLetterPersona", js_content)

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

    def test_09_folder_organization_and_assets(self):
        # Verify profiles folder
        profiles_dir = os.path.join(self.root_dir, "assets", "profiles")
        self.assertTrue(os.path.isdir(profiles_dir), "assets/profiles/ must exist")
        self.assertTrue(os.path.exists(os.path.join(profiles_dir, "alex-morgan-profile.webp")), "Missing alex-morgan-profile.webp in assets/profiles")
        self.assertTrue(os.path.exists(os.path.join(profiles_dir, "stefan-kramer-profile.webp")), "Missing stefan-kramer-profile.webp in assets/profiles")

        # Verify workflows and search_links folder
        workflows_dir = os.path.join(self.root_dir, "workflows")
        self.assertTrue(os.path.isdir(workflows_dir), "workflows/ directory must exist")
        self.assertTrue(os.path.exists(os.path.join(workflows_dir, "daily-job-search-workflow.md")), "workflows/daily-job-search-workflow.md must exist")

        search_links_dir = os.path.join(workflows_dir, "search_links")
        self.assertTrue(os.path.isdir(search_links_dir), "workflows/search_links/ directory must exist")
        for prof in ["designer", "devops", "engineering", "finance"]:
            self.assertTrue(
                os.path.exists(os.path.join(search_links_dir, f"daily-job-search-links-{prof}.md")),
                f"Missing search links for {prof}"
            )

    def test_10_theme_and_button_affordances(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, "html.parser")

        # Verify theme toggle in top-nav
        theme_toggle = soup.find(id="theme-toggle-nav-btn")
        self.assertIsNotNone(theme_toggle, "Missing #theme-toggle-nav-btn in top navigation")

        # Verify .btn-secondary-on-dark is linked to a valid download
        btn_secondary = soup.select_one(".btn-secondary-on-dark")
        self.assertIsNotNone(btn_secondary, "Missing .btn-secondary-on-dark")
        href = btn_secondary.get("href", "")
        self.assertTrue(href.endswith(".zip"), f".btn-secondary-on-dark href must point to zip file, got '{href}'")
        self.assertTrue(btn_secondary.has_attr("download"), ".btn-secondary-on-dark should have download attribute")

    def test_11_github_icons_and_links(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, "html.parser")

        # Hero GitHub link & SVG
        hero_gh = soup.select_one("#hero .btn-hero-gh")
        self.assertIsNotNone(hero_gh, "Missing GitHub link in #hero")
        self.assertEqual(hero_gh.get("href"), "https://github.com/masrisystems/resume-template")
        self.assertIsNotNone(hero_gh.find("svg"), "Hero GitHub button must contain SVG icon")

        # Footer GitHub link & SVG
        footer_gh = soup.select_one("footer .footer-gh-link")
        self.assertIsNotNone(footer_gh, "Missing GitHub link in footer")
        self.assertEqual(footer_gh.get("href"), "https://github.com/masrisystems/resume-template")
        self.assertIsNotNone(footer_gh.find("svg"), "Footer GitHub link must contain SVG icon")

    def test_12_workflow_simulation_deck(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, "html.parser")

        # Simulation controls
        self.assertIsNotNone(soup.find(id="sim-play-btn"), "Missing #sim-play-btn")
        self.assertIsNotNone(soup.find(id="sim-clock"), "Missing #sim-clock")
        self.assertIsNotNone(soup.find(id="workflow-scrub-fill"), "Missing #workflow-scrub-fill")
        self.assertIsNotNone(soup.find(id="sim-stage-monitor"), "Missing #sim-stage-monitor")

        # Verify all 4 stage cards have data-stage
        stage_cards = soup.select(".workflow-stage-card[data-stage]")
        self.assertEqual(len(stage_cards), 4, "Expected 4 workflow-stage-cards with data-stage attribute")

        # Verify hub.js functions
        with open(self.hub_js_path, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertIn("function toggleWorkflowSimulation", js)
        self.assertIn("function renderSimStage", js)
        self.assertIn("function jumpToSimStage", js)

    def test_13_google_flow_prompt_and_simplified_stages(self):
        # 1. Prompt files exist
        prompt_md = os.path.join(self.root_dir, "jobs", "prompts", "google_job_search_flow_prompt.md")
        prompt_txt = os.path.join(self.root_dir, "jobs", "prompts", "google_job_search_flow_prompt.txt")
        self.assertTrue(os.path.exists(prompt_md), "Missing google_job_search_flow_prompt.md")
        self.assertTrue(os.path.exists(prompt_txt), "Missing google_job_search_flow_prompt.txt")

        with open(prompt_md, "r", encoding="utf-8") as f:
            md_text = f.read()
        self.assertIn("Google Dorking", md_text)
        self.assertIn("personio.de", md_text)

        # 2. Check index.html prompt library card
        with open(self.index_path, "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, "html.parser")
        
        prompt_titles = [h3.get_text(strip=True) for h3 in soup.select("#prompts .prompt-card-title")]
        self.assertTrue(any("Google Direct ATS" in title for title in prompt_titles), f"Google Direct ATS prompt card missing from #prompts. Found: {prompt_titles}")

        # 3. Check simplified, accessible stage card titles
        stage_titles = [h3.get_text(strip=True) for h3 in soup.select(".workflow-stage-card .workflow-stage-title")]
        self.assertEqual(len(stage_titles), 4)
        self.assertIn("Spot Fresh Jobs & Skip Old Ones", stage_titles[0])
        self.assertIn("Check Your Fit & Pick The Top 2", stage_titles[1])
        self.assertIn("Auto-Generate Resume & Cover Letter", stage_titles[2])
        self.assertIn("Submit, Record It & You're Done!", stage_titles[3])

    def test_14_responsive_navigation_and_drawer(self):
        with open(self.index_path, "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, "html.parser")

        top_nav = soup.find(id="top-nav")
        self.assertIsNotNone(top_nav, "Missing #top-nav")

        # 1. Nav toggle button
        toggle_btn = top_nav.find(id="nav-toggle-btn")
        self.assertIsNotNone(toggle_btn, "Missing #nav-toggle-btn hamburger button in #top-nav")
        self.assertEqual(toggle_btn.get("aria-controls"), "nav-drawer")
        self.assertEqual(toggle_btn.get("aria-expanded"), "false")
        self.assertIsNotNone(toggle_btn.find(id="nav-icon-menu"), "Missing #nav-icon-menu SVG in toggle button")
        self.assertIsNotNone(toggle_btn.find(id="nav-icon-close"), "Missing #nav-icon-close SVG in toggle button")

        # 2. Mobile Nav Drawer
        drawer = top_nav.find(id="nav-drawer")
        self.assertIsNotNone(drawer, "Missing #nav-drawer element")
        drawer_classes = drawer.get("class", [])
        self.assertIn("nav-drawer", drawer_classes)

        # 3. Drawer Links point to valid sections
        drawer_links = drawer.select("a[href^='#']")
        self.assertGreaterEqual(len(drawer_links), 7, "Mobile drawer must contain at least 7 section anchor links")
        for a in drawer_links:
            anchor_id = a.get("href").lstrip("#")
            self.assertIsNotNone(soup.find(id=anchor_id), f"Drawer link {a.get('href')} points to non-existent ID #{anchor_id}")

        # 4. Drawer contains download CTA
        drawer_cta = drawer.select_one("a[download]")
        self.assertIsNotNone(drawer_cta, "Mobile drawer must contain starter kit download CTA")

        # 5. Check hub.js contains mobile navigation controller functions
        with open(self.hub_js_path, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertIn("function toggleMobileNav", js)
        self.assertIn("function closeMobileNav", js)

if __name__ == "__main__":
    unittest.main()



