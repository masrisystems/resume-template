#!/usr/bin/env python3
"""
Unified Automation Engine for Daily Job Discovery and Application Preparation.

Features:
- init-config: Scaffold a standardized application config JSON from profile SSOT
- build-resume: Generate tailored HTML resume from index.html with DOM parity
- validate-resume: Run strict DOM parity, attribute matching, and anti-hyphen checks
- build-cover-letter: Generate DIN-5008 HTML cover letter from template & profile SSOT
- validate-cover-letter: Run invariant checks, anti-AI burstiness, 8-word JD overlap, and 12-word cross-letter overlap
- build-roles: Compile and validate all canonical role resumes to HTML and PDF
- build-links: Render daily-job-search-links.md from profile SSOT
- export-pdfs: Headless Chrome / Edge PDF generation for resumes and cover letters
- run: Execute end-to-end generation, validation, and PDF export from a single config file
"""

import os
import sys
import json
import re
import glob
import shutil
import argparse
import subprocess
from pathlib import Path
from html.parser import HTMLParser

BASE_DIR = Path(__file__).resolve().parent.parent
JOBS_DIR = BASE_DIR / "jobs"
RESUMES_DIR = JOBS_DIR / "resumes"
COVER_LETTERS_DIR = JOBS_DIR / "cover_letters"
JOB_DESCRIPTIONS_DIR = JOBS_DIR / "job_descriptions"
CONFIGS_DIR = JOBS_DIR / "configs"
ROLES_DIR = JOBS_DIR / "roles"
ROLES_HTML_DIR = ROLES_DIR / "html"
ROLES_PDF_DIR = ROLES_DIR / "pdf"
MASTER_INDEX = BASE_DIR / "index.html"
CONFIG_DIR = BASE_DIR / "config"

# ==========================================
# 0. PROFILE SINGLE SOURCE OF TRUTH (SSOT)
# ==========================================

ACTIVE_PROFILE_PATH = None

def set_active_profile(profile_path):
    global ACTIVE_PROFILE_PATH
    ACTIVE_PROFILE_PATH = profile_path

def load_profile(profile_path=None):
    path = profile_path or ACTIVE_PROFILE_PATH
    if path:
        cfg_file = Path(path)
        if cfg_file.exists():
            return json.loads(cfg_file.read_text(encoding="utf-8"))
    cfg_file = CONFIG_DIR / "profile.json"
    if not cfg_file.exists():
        cfg_file = CONFIG_DIR / "profile.example.json"
    if not cfg_file.exists():
        raise FileNotFoundError("Neither config/profile.json nor config/profile.example.json found.")
    return json.loads(cfg_file.read_text(encoding="utf-8"))


# ==========================================
# 1. DOM PARSER & RESUME VALIDATION
# ==========================================

class DOMStructureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.non_lang_attrs = []
        self.interactive_ids = set()

    def handle_starttag(self, tag, attrs):
        self.tags.append(('start', tag))
        filtered_attrs = []
        attrs_dict = dict(attrs)
        for k, v in attrs:
            if k in ('data-lang-en', 'data-lang-de'):
                continue
            if tag == 'meta' and k == 'content' and ('og:title' in attrs_dict.values() or 'twitter:title' in attrs_dict.values()):
                continue
            if k == 'id':
                self.interactive_ids.add(v)
            filtered_attrs.append((k, v))
        self.non_lang_attrs.append((tag, tuple(sorted(filtered_attrs))))

    def handle_endtag(self, tag):
        self.tags.append(('end', tag))


def validate_resume_file(tailored_path, master_path=MASTER_INDEX):
    tailored_path = Path(tailored_path)
    master_path = Path(master_path)

    if not tailored_path.exists():
        raise FileNotFoundError(f"Tailored resume file not found: {tailored_path}")
    if not master_path.exists():
        raise FileNotFoundError(f"Master index file not found: {master_path}")

    master_html = master_path.read_text(encoding="utf-8")
    tailored_html = tailored_path.read_text(encoding="utf-8")

    # 1. Check prohibited domains from profile
    profile = load_profile()
    prohibited = profile.get("candidate", {}).get("prohibited_domains", [])
    for dom in prohibited:
        if dom in tailored_html:
            raise ValueError(f"Prohibited domain '{dom}' found in {tailored_path}")

    # 2. Check hyphenated compounds
    banned_hyphens = [
        r'\bREST-APIs?\b',
        r'\bFigma-Designs?\b',
        r'\bCI/CD-Pipelines?\b',
        r'\bn8n-Workflows?\b',
        r'\bMCP-Tools?\b',
        r'\bMCP-Servers?\b',
        r'\bKI-Agenten?\b',
        r'\bFullstack-Entwickler\b',
        r'\bFull-Stack-Entwickler\b',
        r'\bFull-Stack Developer\b',
        r'\bFull-Stack Engineer\b',
        r'\bCloud-Architekturen?\b',
    ]
    for pat in banned_hyphens:
        m = re.search(pat, tailored_html, re.IGNORECASE)
        if m:
            raise ValueError(f"Found banned hyphenated technical term '{m.group(0)}' in {tailored_path}")

    # 3. Check byte-identical script and style blocks
    master_scripts = re.findall(r'<script.*?</script>', master_html, re.DOTALL)
    tailored_scripts = re.findall(r'<script.*?</script>', tailored_html, re.DOTALL)
    if len(master_scripts) != len(tailored_scripts):
        raise ValueError(f"Script block count mismatch: master has {len(master_scripts)}, tailored has {len(tailored_scripts)}")
    for idx, (ms, ts) in enumerate(zip(master_scripts, tailored_scripts)):
        if ms != ts:
            raise ValueError(f"Script block {idx} differs between master and {tailored_path}")

    master_styles = re.findall(r'<style.*?</style>', master_html, re.DOTALL)
    tailored_styles = re.findall(r'<style.*?</style>', tailored_html, re.DOTALL)
    if len(master_styles) != len(tailored_styles):
        raise ValueError(f"Style block count mismatch: master has {len(master_styles)}, tailored has {len(tailored_styles)}")
    for idx, (ms, ts) in enumerate(zip(master_styles, tailored_styles)):
        if ms != ts:
            raise ValueError(f"Style block {idx} differs between master and {tailored_path}")

    # 4. Check DOM tag sequence and non-language attributes
    master_parser = DOMStructureParser()
    master_parser.feed(master_html)

    tailored_parser = DOMStructureParser()
    tailored_parser.feed(tailored_html)

    if master_parser.tags != tailored_parser.tags:
        raise ValueError(f"DOM tag sequence does not match master in {tailored_path}")
    if master_parser.non_lang_attrs != tailored_parser.non_lang_attrs:
        raise ValueError(f"Non-language attributes do not match master in {tailored_path}")

    # 5. Check interactive IDs
    expected_ids = {
        'resumeContent', 'header', 'work-experience', 'current-role', 'brainkets-role',
        'side-projects-role', 'technical-skills', 'education', 'academic-achievements',
        'languages', 'footer', 'theme-toggle', 'downloadPdf'
    }
    missing_ids = expected_ids - tailored_parser.interactive_ids
    if missing_ids:
        raise ValueError(f"Missing required interactive IDs in {tailored_path}: {missing_ids}")

    print(f"[OK] Resume Validation PASSED: {tailored_path.name}")
    return True

# ==========================================
# 2. RESUME GENERATION
# ==========================================

def get_resume_config(config):
    if "role_profile" in config:
        role_id = config["role_profile"]
        role_file = ROLES_DIR / f"{role_id}.json"
        if not role_file.exists():
            raise FileNotFoundError(f"Role profile '{role_id}' not found: {role_file}")
        role_data = json.loads(role_file.read_text(encoding="utf-8"))
        if "resume" in config and isinstance(config["resume"], dict):
            merged = dict(role_data)
            merged.update(config["resume"])
            return merged
        return role_data
    elif "resume" in config:
        return config["resume"]
    else:
        raise KeyError("Config must contain either 'role_profile' or 'resume'")

def generate_resume_html(res_cfg, master_html=None):
    if master_html is None:
        master_html = MASTER_INDEX.read_text(encoding="utf-8")
    c = master_html

    profile = load_profile()
    cand_name = profile.get("candidate", {}).get("name", "Alex Morgan")

    # 1. Title & Meta
    default_title = f"{cand_name} | {res_cfg.get('subtitle_de', 'Fullstack Developer')} — Resume"
    raw_title = res_cfg.get("title", default_title)
    title = raw_title.replace("{candidate_name}", cand_name)

    raw_og = res_cfg.get("og_title", title.split(" — ")[0])
    og_title = raw_og.replace("{candidate_name}", cand_name)

    raw_tw = res_cfg.get("twitter_title", og_title)
    twitter_title = raw_tw.replace("{candidate_name}", cand_name)

    c = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', c, count=1)
    c = re.sub(r'<meta property="og:title" content=".*?" />', f'<meta property="og:title" content="{og_title}" />', c, count=1)
    c = re.sub(r'<meta name="twitter:title" content=".*?" />', f'<meta name="twitter:title" content="{twitter_title}" />', c, count=1)

    # 2. Subtitle
    sub_de = res_cfg["subtitle_de"]
    sub_en = res_cfg["subtitle_en"]
    new_sub = f'''          <p class="mt-1 font-semibold text-[#a9583e] dark:text-[#e8a55a]"
            data-lang-en="{sub_en}"
            data-lang-de="{sub_de}">
            {sub_en}
          </p>'''
    sub_re = r'          <p class="mt-1 font-semibold text-\[#a9583e\] dark:text-\[#e8a55a\]".*?</p>'
    if not re.search(sub_re, c, re.DOTALL):
        raise ValueError("Could not find subtitle block in master index.html")
    c = re.sub(sub_re, new_sub, c, count=1, flags=re.DOTALL)

    # 3. Summary
    sum_de = res_cfg["summary_de"]
    sum_en = res_cfg["summary_en"]
    new_sum = f'''          <p class="mt-2 max-w-2xl text-sm text-gray-700 dark:text-gray-300"
            data-lang-en="{sum_en}"
            data-lang-de="{sum_de}">
            {sum_en}
          </p>'''
    sum_re = r'          <p class="mt-2 max-w-2xl text-sm text-gray-700 dark:text-gray-300".*?</p>'
    if not re.search(sum_re, c, re.DOTALL):
        raise ValueError("Could not find summary block in master index.html")
    c = re.sub(sum_re, new_sum, c, count=1, flags=re.DOTALL)

    # Helper for skills block
    def make_skills_block(heading_en, heading_de, heading_display, items):
        lis = "\n".join(f"            <li>{it}</li>" for it in items)
        return f'''        <div>
          <h4 class="font-semibold" data-lang-en="{heading_en}" data-lang-de="{heading_de}">
            {heading_display}
          </h4>
          <ul class="list-disc ml-5">
{lis}
          </ul>
        </div>'''

    # 4. Frontend Block (Must preserve exactly 2 <li> items)
    front_cfg = res_cfg["skills_frontend"]
    if len(front_cfg["items"]) != 2:
        raise ValueError(f"skills_frontend must have exactly 2 items to preserve DOM parity, got {len(front_cfg['items'])}")
    new_front = make_skills_block(front_cfg["heading_en"], front_cfg["heading_de"], front_cfg["heading_display"], front_cfg["items"])
    front_re = r'        <div>\s*<h4 class="font-semibold" data-lang-en="Frontend \(Primary\)" data-lang-de="Frontend \(Primär\)">.*?</ul>\s*</div>'
    c = re.sub(front_re, new_front, c, count=1, flags=re.DOTALL)

    # 5. Backend Block (Must preserve exactly 4 <li> items)
    back_cfg = res_cfg["skills_backend"]
    if len(back_cfg["items"]) != 4:
        raise ValueError(f"skills_backend must have exactly 4 items to preserve DOM parity, got {len(back_cfg['items'])}")
    new_back = make_skills_block(back_cfg["heading_en"], back_cfg["heading_de"], back_cfg["heading_display"], back_cfg["items"])
    back_re = r'        <div>\s*<h4 class="font-semibold" data-lang-en="Backend \(Primary\)" data-lang-de="Backend \(Primär\)">.*?</ul>\s*</div>'
    c = re.sub(back_re, new_back, c, count=1, flags=re.DOTALL)

    # 6. DevOps Block (Must preserve exactly 5 <li> items)
    dev_cfg = res_cfg["skills_devops"]
    if len(dev_cfg["items"]) != 5:
        raise ValueError(f"skills_devops must have exactly 5 items to preserve DOM parity, got {len(dev_cfg['items'])}")
    new_dev = make_skills_block(dev_cfg["heading_en"], dev_cfg["heading_de"], dev_cfg["heading_display"], dev_cfg["items"])
    dev_re = r'        <div>\s*<h4 class="font-semibold" data-lang-en="DevOps & Tools" data-lang-de="DevOps & Werkzeuge">.*?</ul>\s*</div>'
    c = re.sub(dev_re, new_dev, c, count=1, flags=re.DOTALL)

    # 7. Secondary Block (Must preserve exactly 2 <li> items)
    sec_cfg = res_cfg["skills_secondary"]
    if len(sec_cfg["items"]) != 2:
        raise ValueError(f"skills_secondary must have exactly 2 items to preserve DOM parity, got {len(sec_cfg['items'])}")
    new_sec = make_skills_block(sec_cfg["heading_en"], sec_cfg["heading_de"], sec_cfg["heading_display"], sec_cfg["items"])
    sec_re = r'        <div>\s*<h4 class="font-semibold" data-lang-en="Secondary / Previous Stack" data-lang-de="Sekundär-Stack &amp; Frühere Technologien">.*?</ul>\s*</div>'
    c = re.sub(sec_re, new_sec, c, count=1, flags=re.DOTALL)

    # Clean specific software versions
    c = c.replace('Shopware 6.6', 'Shopware')
    c = c.replace('Laravel 12 / Vue 3 / Inertia', 'Laravel / Vue.js / Inertia')
    c = c.replace('Vue.js 3', 'Vue.js')
    c = c.replace('Vue 3', 'Vue.js')
    return c

def sync_stylesheets():
    style_src = BASE_DIR / "style.css"
    if style_src.exists():
        ROLES_HTML_DIR.mkdir(parents=True, exist_ok=True)
        RESUMES_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(style_src, ROLES_HTML_DIR / "style.css")
        shutil.copy2(style_src, RESUMES_DIR / "style.css")

def build_resume_from_config(config_path):
    sync_stylesheets()
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    slug = config["slug"]
    res_cfg = get_resume_config(config)

    c = generate_resume_html(res_cfg)

    # Output file
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RESUMES_DIR / f"{slug}.html"
    out_file.write_text(c, encoding="utf-8")
    print(f"[OK] Wrote Tailored Resume: {out_file}")

    # Immediate validation
    validate_resume_file(out_file)
    return out_file

def build_role(role_path_or_id):
    sync_stylesheets()
    if isinstance(role_path_or_id, Path):
        role_file = role_path_or_id
    else:
        role_file = ROLES_DIR / f"{role_path_or_id}.json"

    if not role_file.exists():
        raise FileNotFoundError(f"Role config not found: {role_file}")

    profile = load_profile()
    cand_name = profile.get("candidate", {}).get("name", "Alex Morgan")
    cand_slug = cand_name.replace(" ", "_").replace("-", "_").replace(".", "").replace("/", "")

    role_cfg = json.loads(role_file.read_text(encoding="utf-8"))
    role_id = role_cfg.get("role_id", role_file.stem)

    c = generate_resume_html(role_cfg)

    ROLES_HTML_DIR.mkdir(parents=True, exist_ok=True)
    out_html = ROLES_HTML_DIR / f"{role_id}.html"
    out_html.write_text(c, encoding="utf-8")
    print(f"[OK] Wrote Role HTML: {out_html.name}")

    validate_resume_file(out_html)

    ROLES_PDF_DIR.mkdir(parents=True, exist_ok=True)
    out_pdf = ROLES_PDF_DIR / f"{cand_slug}_Lebenslauf_{role_id}.pdf"
    browser_exe = find_browser()
    html_to_pdf(browser_exe, out_html, out_pdf)
    print(f"[OK] Wrote Role PDF: {out_pdf.name}")
    return out_html, out_pdf

def build_all_roles(specific_role=None):
    if specific_role:
        print(f"\n=== Building Canonical Role Resume: {specific_role} ===")
        return [build_role(specific_role)]

    print("\n=== Building and Validating All Canonical Role Resumes ===")
    ROLES_DIR.mkdir(parents=True, exist_ok=True)
    role_files = sorted(ROLES_DIR.glob("*.json"))
    if not role_files:
        raise FileNotFoundError(f"No role definitions found in {ROLES_DIR}")

    results = []
    for rf in role_files:
        print(f"\nProcessing Role: {rf.stem}")
        h, p = build_role(rf)
        results.append((rf.stem, h, p))

    print(f"\n[SUCCESS] Successfully compiled and verified {len(results)} canonical roles!\n")
    return results


# ==========================================
# 3. COVER LETTER TEMPLATING & VALIDATION
# ==========================================

DIN_5008_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Bewerbung - {candidate_name} - {company_clean}</title>
<style>
@page {
    size: A4;
    margin: 0;
}
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #1e293b;
    background-color: #ffffff;
    width: 210mm;
    height: 297mm;
    padding: 24mm 22mm 20mm 25mm;
    position: relative;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
.header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1.5px solid #e2e8f0;
    padding-bottom: 12px;
    margin-bottom: 22px;
}
.sender-name {
    font-size: 16pt;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
}
.sender-title {
    font-size: 9.5pt;
    font-weight: 600;
    color: #a9583e;
    margin-top: 2px;
}
.sender-contact {
    text-align: right;
    font-size: 8.5pt;
    color: #475569;
    line-height: 1.45;
}
.sender-contact a {
    color: #a9583e;
    text-decoration: none;
}
.recipient-date-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 24px;
}
.recipient-block {
    font-size: 9.5pt;
    line-height: 1.45;
    color: #334155;
}
.recipient-company {
    font-weight: 600;
    color: #0f172a;
}
.date-block {
    font-size: 9pt;
    color: #64748b;
}
.subject-line {
    font-size: 12pt;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 16px;
    letter-spacing: -0.01em;
}
.salutation {
    font-weight: 600;
    margin-bottom: 12px;
    color: #0f172a;
}
.paragraph {
    margin-bottom: 13px;
    text-align: justify;
}
.paragraph a {
    color: #a9583e;
    text-decoration: none;
}
.closing {
    margin-top: 18px;
    margin-bottom: 24px;
}
.signature-name {
    font-weight: 700;
    font-size: 11pt;
    color: #0f172a;
}
.footer-note {
    position: absolute;
    bottom: 12mm;
    left: 25mm;
    right: 22mm;
    border-top: 1px solid #e2e8f0;
    padding-top: 8px;
    font-size: 8pt;
    color: #94a3b8;
    display: flex;
    justify-content: space-between;
}
.footer-note a {
    color: #a9583e;
    text-decoration: none;
}
</style>
</head>
<body>
<div class="header-row">
    <div>
        <div class="sender-name">{candidate_name}</div>
        <div class="sender-title">{sender_title}</div>
    </div>
    <div class="sender-contact">
        {candidate_address}<br>
        {candidate_phone} · <a href="mailto:{candidate_email}">{candidate_email}</a><br>
        <a href="{candidate_links}">{candidate_links}</a>
    </div>
</div>

<div class="recipient-date-row">
    <div class="recipient-block">
        <div class="recipient-company">{recipient_company}</div>
        {recipient_person_div}
        <div>{recipient_address}</div>
    </div>
    <div class="date-block">
        {date_formatted}
    </div>
</div>

<div class="subject-line">{subject_line}</div>

<div class="salutation">{salutation}</div>

{paragraphs_html}

<div class="closing">
    <div>Mit freundlichen Grüßen</div>
    <div style="margin-top: 14px;" class="signature-name">{candidate_name}</div>
</div>

<div class="footer-note">
    <span>Bewerbungsunterlagen · {candidate_name}</span>
    <span>Portfolio: <a href="{candidate_links}">{candidate_links_display}</a></span>
</div>
</body>
</html>
"""

def format_german_date(date_str, location="Berlin"):
    months = {
        "01": "Januar", "02": "Februar", "03": "März", "04": "April",
        "05": "Mai", "06": "Juni", "07": "Juli", "08": "August",
        "09": "September", "10": "Oktober", "11": "November", "12": "Dezember"
    }
    parts = date_str.split("-")
    if len(parts) == 3:
        year, month, day = parts
        day_int = int(day)
        month_de = months.get(month, month)
        return f"{location}, {day_int}. {month_de} {year}"
    return f"{location}, {date_str}"

def get_ngrams(tokens, n):
    return set(" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1))

def validate_cover_letter_file(cl_path, jd_path=None):
    cl_path = Path(cl_path)
    if not cl_path.exists():
        raise FileNotFoundError(f"Cover letter file not found: {cl_path}")

    profile = load_profile()
    cand = profile.get("candidate", {})
    invariants = profile.get("invariants", {})

    content = cl_path.read_text(encoding="utf-8")
    paras = re.findall(r'<div class="paragraph">(.*?)</div>', content, re.DOTALL)
    if not paras:
        raise ValueError(f"No <div class=\"paragraph\"> elements found in {cl_path}")

    body_text = " ".join(re.sub(r"<[^>]+>", "", p) for p in paras)
    words = body_text.split()

    # 1. Word count
    if len(words) >= 300:
        raise ValueError(f"Word count {len(words)} >= 300 limit in {cl_path}")

    # 2. Strict Invariants from Profile
    for dom in cand.get("prohibited_domains", []):
        if dom in content:
            raise ValueError(f"Prohibited domain '{dom}' found in {cl_path}")

    portfolio_link = cand.get("links_url", cand.get("portfolio_url", ""))
    if portfolio_link and portfolio_link not in content:
        raise ValueError(f"Portfolio link '{portfolio_link}' missing in {cl_path}")

    sal_phrase = invariants.get("target_salary_phrase_de", "")
    if sal_phrase and sal_phrase not in content:
        raise ValueError(f"Target compensation invariant '{sal_phrase}' missing in {cl_path}")

    if not (("Kündigungsfrist" in content or "Kündigung" in content) and "Monatsende" in content):
        raise ValueError(f"Notice period invariant ('Kündigungsfrist' and 'Monatsende') missing in {cl_path}")

    # 2b. CSS & Template Syntax Invariants
    if "{{" in content or "}}" in content:
        raise ValueError(f"Unrendered double curly braces found in {cl_path}")

    for req_css in ["@page {", "size: A4;", "body {", ".header-row {", ".footer-note {"]:
        if req_css not in content:
            raise ValueError(f"Required CSS rule '{req_css}' missing in {cl_path}")

    # 3. Anti-AI Formatting Rules (checked against body_text)
    if "—" in body_text or "–" in body_text:
        raise ValueError(f"Em/en dashes found in cover letter body {cl_path.name}. Use hyphens or rephrase.")
    if ";" in body_text:
        raise ValueError(f"Semicolon found in cover letter body {cl_path.name}. Simplify sentence structure.")
    if any(q in body_text for q in ["“", "”", "„", "«", "»"]):
        raise ValueError(f"Curved quotes found in {cl_path.name}. Use straight quotes only.")

    # 4. Banned Filler Words (checked against body_text)
    banned_fillers = [
        r'\bdelve\b', r'\bleverage\b', r'\butilize\b', r'\brobust\b',
        r'\bcomprehensive\b', r'\bstreamline\b', r'\bfurthermore\b',
        r'\bmoreover\b', r'\bit is important to note\b'
    ]
    for b in banned_fillers:
        if re.search(b, body_text, re.IGNORECASE):
            raise ValueError(f"Banned buzzword pattern '{b}' detected in {cl_path.name}")

    # 5. Sentence Burstiness Variance
    sentences = [s.strip() for s in re.split(r'[.!?]+', body_text) if s.strip()]
    sentence_lengths = [len(s.split()) for s in sentences]
    if sentence_lengths:
        variance_range = max(sentence_lengths) - min(sentence_lengths)
        has_punchy = any(l <= 5 for l in sentence_lengths)
        if variance_range < 20:
            print(f"[WARN] Sentence length range ({variance_range} words) is below recommended 20-word floor in {cl_path.name}")
        if not has_punchy:
            print(f"[WARN] No punchy sentence (<= 5 words) found in {cl_path.name}")

    # 6. 8-Word JD Overlap Check
    tokens = re.sub(r"[^\w\s]", " ", body_text).lower().split()
    cl_8grams = get_ngrams(tokens, 8)

    if jd_path and Path(jd_path).exists():
        jd_text = Path(jd_path).read_text(encoding="utf-8")
        jd_tokens = re.sub(r"[^\w\s]", " ", jd_text).lower().split()
        jd_8grams = get_ngrams(jd_tokens, 8)
        jd_common = cl_8grams.intersection(jd_8grams)
        if jd_common:
            raise ValueError(f"8-word sequence overlap with job description in {cl_path}: {jd_common}")
    else:
        stem = cl_path.stem
        slug = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', stem)
        cand_jd = JOB_DESCRIPTIONS_DIR / f"{slug}.txt"
        if cand_jd.exists():
            jd_text = cand_jd.read_text(encoding="utf-8")
            jd_tokens = re.sub(r"[^\w\s]", " ", jd_text).lower().split()
            jd_8grams = get_ngrams(jd_tokens, 8)
            jd_common = cl_8grams.intersection(jd_8grams)
            if jd_common:
                raise ValueError(f"8-word sequence overlap with job description ({cand_jd.name}) in {cl_path}: {jd_common}")

    # 7. 12-Word Cross-Cover Letter Overlap Check
    cl_12grams = get_ngrams(tokens, 12)
    all_other_cls = glob.glob(str(COVER_LETTERS_DIR / "*.html"))
    for other in all_other_cls:
        if Path(other).resolve() == cl_path.resolve():
            continue
        try:
            c2 = Path(other).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        p2 = re.findall(r'<div class="paragraph">(.*?)</div>', c2, re.DOTALL)
        t2 = re.sub(r"[^\w\s]", " ", " ".join(re.sub(r"<[^>]+>", "", p) for p in p2)).lower().split()
        ng2 = get_ngrams(t2, 12)
        common = cl_12grams.intersection(ng2)
        if common:
            raise ValueError(f"12-word cover letter body overlap between {cl_path.name} and {Path(other).name}: {common}")

    print(f"[OK] Cover Letter Validation PASSED: {cl_path.name} ({len(words)} words)")
    return True

def build_cover_letter_from_config(config_path):
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    slug = config["slug"]
    date_str = config["date"]
    cl_cfg = config["cover_letter"]

    profile = load_profile()
    cand = profile.get("candidate", {})
    inv = profile.get("invariants", {})

    cand_name = cand.get("name", "Alex Morgan")
    cand_addr = f"{cand.get('address_street', 'Musterstraße 123')} · {cand.get('address_city', '10115 Berlin')}"
    cand_phone = cand.get("phone", "+49 151 12345678")
    cand_email = cand.get("email", "alex.morgan@example.com")
    cand_links = cand.get("links_url", cand.get("portfolio_url", "https://links.example.com"))
    cand_links_display = re.sub(r'^https?://', '', cand_links).rstrip('/')
    loc_city = inv.get("default_location_city", "Berlin")

    recipient_person = cl_cfg.get("recipient_person", "")
    recipient_person_div = f"<div>{recipient_person}</div>" if recipient_person else ""

    paragraphs_html = "\n\n".join(
        f'<div class="paragraph">\n{p.strip()}\n</div>' for p in cl_cfg["paragraphs"]
    )

    replacements = {
        "{candidate_name}": cand_name,
        "{candidate_address}": cand_addr,
        "{candidate_phone}": cand_phone,
        "{candidate_email}": cand_email,
        "{candidate_links}": cand_links,
        "{candidate_links_display}": cand_links_display,
        "{company_clean}": cl_cfg["company_clean"],
        "{sender_title}": cl_cfg.get("sender_title", cand.get("title_de", "Senior Fullstack Entwickler")),
        "{recipient_company}": cl_cfg["recipient_company"],
        "{recipient_person_div}": recipient_person_div,
        "{recipient_address}": cl_cfg["recipient_address"],
        "{date_formatted}": format_german_date(date_str, location=loc_city),
        "{subject_line}": cl_cfg["subject_line"],
        "{salutation}": cl_cfg["salutation"],
        "{paragraphs_html}": paragraphs_html
    }
    html = DIN_5008_TEMPLATE
    for k, v in replacements.items():
        html = html.replace(k, v)

    COVER_LETTERS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = COVER_LETTERS_DIR / f"{date_str}_{slug}.html"
    out_file.write_text(html, encoding="utf-8")
    print(f"[OK] Wrote Cover Letter HTML: {out_file}")

    # Immediate validation
    validate_cover_letter_file(out_file)
    return out_file

# ==========================================
# 4. HEADLESS PDF EXPORT
# ==========================================

def find_browser():
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("chrome"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        shutil.which("msedge"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    raise RuntimeError("No headless Chrome or Edge browser executable found on this system.")

def html_to_pdf(browser_exe, input_html, output_pdf):
    input_html = Path(input_html).resolve()
    output_pdf = Path(output_pdf).resolve()

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    file_url = input_html.as_uri()

    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={str(output_pdf)}",
        file_url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if not output_pdf.exists() or output_pdf.stat().st_size == 0:
        raise RuntimeError(f"Failed to generate PDF for {input_html}.\nOutput: {result.stdout}\nError: {result.stderr}")

    print(f"[OK] Generated PDF: {output_pdf.name} ({output_pdf.stat().st_size} bytes)")
    return output_pdf

def export_pdfs(company_slug=None, date_str=None, all_files=False):
    sync_stylesheets()
    browser_exe = find_browser()

    if company_slug and date_str:
        # 1. Resume
        res_html = RESUMES_DIR / f"{company_slug}.html"
        if res_html.exists():
            res_pdf_slug = RESUMES_DIR / f"{company_slug}.pdf"
            html_to_pdf(browser_exe, res_html, res_pdf_slug)
            res_pdf_dated = RESUMES_DIR / f"{date_str}_{company_slug}.pdf"
            shutil.copy2(res_pdf_slug, res_pdf_dated)
            print(f"[OK] Copied dated Resume PDF: {res_pdf_dated.name}")

        # 2. Cover Letter
        cl_html = COVER_LETTERS_DIR / f"{date_str}_{company_slug}.html"
        if cl_html.exists():
            cl_pdf = COVER_LETTERS_DIR / f"{date_str}_{company_slug}.pdf"
            html_to_pdf(browser_exe, cl_html, cl_pdf)

    elif date_str:
        for cl in sorted(COVER_LETTERS_DIR.glob(f"{date_str}_*.html")):
            slug = cl.stem[len(date_str) + 1:]
            export_pdfs(company_slug=slug, date_str=date_str)

    elif all_files:
        for cl in sorted(COVER_LETTERS_DIR.glob("*.html")):
            html_to_pdf(browser_exe, cl, cl.with_suffix(".pdf"))
        for res in sorted(RESUMES_DIR.glob("*.html")):
            html_to_pdf(browser_exe, res, res.with_suffix(".pdf"))

# ==========================================
# 5. CLI INTERFACE & SSOT GENERATORS
# ==========================================

def init_config(slug, date_str, role_id="fullstack_laravel"):
    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = CONFIGS_DIR / f"{date_str}_{slug}.json"
    if out_file.exists():
        print(f"[WARN] Config already exists: {out_file}")
        return out_file

    profile = load_profile()
    cand = profile.get("candidate", {})
    inv = profile.get("invariants", {})
    sal_phrase = inv.get("target_salary_phrase_de", "65.000 Euro brutto im Jahr")
    notice_phrase = inv.get("notice_period_de", "dreimonatigen Kündigungsfrist zum Monatsende, im Einvernehmen gern auch kurzfristiger")
    sender_title = cand.get("title_de", "Senior Fullstack Entwickler · PHP, Laravel & Vue.js")
    city = inv.get("default_location_city", "Berlin")

    skeleton = {
        "slug": slug,
        "date": date_str,
        "role_profile": role_id,
        "cover_letter": {
            "company_clean": f"{slug.capitalize()} GmbH",
            "sender_title": sender_title,
            "recipient_company": f"{slug.capitalize()} GmbH",
            "recipient_person": "Recruiting Team",
            "recipient_address": f"Musterstraße 1 · {city}",
            "subject_line": "Bewerbung als Senior Fullstack Engineer (m/w/d)",
            "salutation": "Sehr geehrte Damen und Herren,",
            "paragraphs": [
                f"Technologische Exzellenz und moderne Architekturen bilden das Fundament robuster Softwarelösungen. Die Ausrichtung von {slug.capitalize()} GmbH passt ideal zu meinem Profil.",
                "Seit über fünf Jahren entwickle und skaliere ich moderne Webanwendungen auf Basis von PHP, Laravel, TypeScript und Vue.js. Ein starker Fokus liegt dabei auf sauberen Schnittstellen, automatisierten Tests und CI/CD-Pipelines.",
                f"Meinen Gehaltsrahmen beziffere ich mit {sal_phrase}. Meine Verfügbarkeit richtet sich nach einer {notice_phrase}. Detaillierte Arbeitsproben finden Sie unter {cand.get('links_url', 'https://links.example.com')}. Ich freue mich auf den fachlichen Austausch."
            ]
        }
    }

    out_file.write_text(json.dumps(skeleton, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Initialized skeleton config with role '{role_id}': {out_file}")
    return out_file

def build_daily_search_links(output_file=None):
    profile = load_profile()
    cand = profile.get("candidate", {})
    inv = profile.get("invariants", {})
    sp = profile.get("search_preferences", {})
    platforms = profile.get("search_platforms", [])
    best_practices = profile.get("best_practices", [])

    target_stack = ", ".join(sp.get("target_stack", []))
    exp_level = sp.get("experience_level", "Senior Level (5+ Jahre Erfahrung)")
    location = sp.get("location", "Berlin")
    postal_code = sp.get("postal_code", "10115")
    radius_km = sp.get("radius_km", 25)
    remote_focus = sp.get("remote_focus", "100% Remote (Deutschland/Europa) oder Hybrid Berlin")
    sal_band = sp.get("salary_band", {})
    min_eur = sal_band.get("min_eur", 60000)
    max_eur = sal_band.get("max_eur", 75000)
    target_phrase = inv.get("target_salary_phrase_de", "65.000 Euro brutto im Jahr")
    role_keyword = sp.get("role_keyword") or (cand.get("title_en", "Developer").split()[0])
    
    import urllib.parse
    role_quoted = urllib.parse.quote_plus(role_keyword)
    loc_quoted = urllib.parse.quote_plus(location)

    table_rows = []
    for idx, p in enumerate(platforms, 1):
        name = p.get("name", "Platform")
        cat = p.get("category", "")
        tmpl = p.get("url_template", "")
        rendered_url = (
            tmpl.replace("{role}", role_quoted)
                .replace("{location}", loc_quoted)
                .replace("{postal_code}", postal_code)
                .replace("{radius_km}", str(radius_km))
        )
        table_rows.append(f"| **{idx}** | **{name}** | {cat} · {location} (+{radius_km} km) | [Direktlink]({rendered_url}) |")

    bp_items = "\n".join(f"- {bp}" for bp in best_practices)

    content = f"""---
tags: [career, job-search, daily-routine, links, queries, web-resume]
title: Daily Job Discovery Quick-Links & Saved Search Queries
created: 2026-10-01
---

# 🔎 Daily Job Discovery Quick-Links & Direct Search Queries

Dieses Dokument dient als tägliches Schnellstart-Dashboard für die manuelle und automatisierte Jobrecherche. Alle Links und Parameter werden zentral aus der Profilkonfiguration gesteuert:

- **Kandidat:** {cand.get('name', 'Alex Morgan')} ({cand.get('title_de', cand.get('title_en', 'Software Engineer'))})
- **Zielstack:** {target_stack}
- **Erfahrungslevel:** {exp_level}
- **Region:** {location} ({postal_code}, Umkreis {radius_km} km) sowie {remote_focus}
- **Gehaltsband-Fokus:** {min_eur:,} € – {max_eur:,} € (Ziel: {target_phrase})

---

## ⚡ Schnellstart: Das 10-Minuten-Morgen-Set

| # | Plattform | Kategorie & Parameter | Direktlink |
| :-: | :--- | :--- | :--- |
""" + "\n".join(table_rows) + f"""

---

## 💡 Best Practices für die tägliche Bewerbungsroutine

{bp_items}
"""

    out_path = Path(output_file) if output_file else (BASE_DIR / "daily-job-search-links.md")
    out_path.write_text(content, encoding="utf-8")
    print(f"[OK] Rendered SSOT Daily Search Links: {out_path.name}")
    return out_path

def run_end_to_end(config_path):
    print(f"\n=== Executing End-to-End Application Package from {config_path} ===")
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    slug = config["slug"]
    date_str = config["date"]

    # 1. Resume
    build_resume_from_config(config_path)

    # 2. Cover Letter
    build_cover_letter_from_config(config_path)

    # 3. PDF Export
    export_pdfs(company_slug=slug, date_str=date_str)

    print(f"\n[SUCCESS] All application assets generated, validated, and exported for {slug} ({date_str})!\n")

def main():
    parser = argparse.ArgumentParser(description="Unified Daily Job Application Engine")
    parser.add_argument("--profile", help="Path to profile JSON (default: config/profile.json or config/profile.example.json)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init-config
    p_init = subparsers.add_parser("init-config", help="Initialize a skeleton JSON config")
    p_init.add_argument("--slug", required=True, help="Company slug")
    p_init.add_argument("--date", required=True, help="Application date (YYYY-MM-DD)")
    p_init.add_argument("--role", default="fullstack_laravel", help="Canonical role profile ID (default: fullstack_laravel)")

    # build-roles
    p_roles = subparsers.add_parser("build-roles", help="Build and validate canonical role resumes and export PDFs")
    p_roles.add_argument("--role", help="Specific role ID to build (default: all)")

    # build-links
    p_links = subparsers.add_parser("build-links", help="Render daily-job-search-links.md from profile SSOT")
    p_links.add_argument("--output", help="Optional output markdown filepath")

    # build-resume
    p_res = subparsers.add_parser("build-resume", help="Generate tailored HTML resume from config")
    p_res.add_argument("--config", required=True, help="Path to config JSON")

    # validate-resume
    p_vres = subparsers.add_parser("validate-resume", help="Validate resume HTML file against master")
    p_vres.add_argument("--file", help="Path to resume HTML file")
    p_vres.add_argument("--slug", help="Company slug (looks in jobs/resumes/<slug>.html)")

    # build-cover-letter
    p_cl = subparsers.add_parser("build-cover-letter", help="Generate DIN-5008 cover letter from config")
    p_cl.add_argument("--config", required=True, help="Path to config JSON")

    # validate-cover-letter
    p_vcl = subparsers.add_parser("validate-cover-letter", help="Validate DIN-5008 cover letter")
    p_vcl.add_argument("--file", help="Path to cover letter HTML file")
    p_vcl.add_argument("--date", help="Validate all cover letters for a specific date (YYYY-MM-DD)")
    p_vcl.add_argument("--all", action="store_true", help="Validate all cover letters in jobs/cover_letters/")

    # export-pdfs
    p_pdf = subparsers.add_parser("export-pdfs", help="Generate PDFs via headless browser")
    p_pdf.add_argument("--config", help="Path to config JSON")
    p_pdf.add_argument("--slug", help="Company slug")
    p_pdf.add_argument("--date", help="Application date (YYYY-MM-DD)")
    p_pdf.add_argument("--all", action="store_true", help="Export all resumes and cover letters")

    # run (end-to-end)
    p_run = subparsers.add_parser("run", help="Run full pipeline: build, validate, and export PDFs")
    p_run.add_argument("--config", required=True, help="Path to config JSON")

    args = parser.parse_args()

    if args.profile:
        set_active_profile(args.profile)

    if args.command == "init-config":
        init_config(args.slug, args.date, role_id=args.role)
    elif args.command == "build-roles":
        build_all_roles(specific_role=args.role)
    elif args.command == "build-links":
        build_daily_search_links(output_file=getattr(args, "output", None))
    elif args.command == "build-resume":
        build_resume_from_config(args.config)
    elif args.command == "validate-resume":
        target = args.file if args.file else (RESUMES_DIR / f"{args.slug}.html")
        validate_resume_file(target)
    elif args.command == "build-cover-letter":
        build_cover_letter_from_config(args.config)
    elif args.command == "validate-cover-letter":
        if args.file:
            validate_cover_letter_file(args.file)
        elif args.date:
            for f in sorted(COVER_LETTERS_DIR.glob(f"{args.date}_*.html")):
                validate_cover_letter_file(f)
        elif args.all:
            for f in sorted(COVER_LETTERS_DIR.glob("*.html")):
                validate_cover_letter_file(f)
    elif args.command == "export-pdfs":
        slug = args.slug
        date_str = args.date
        if args.config:
            cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
            slug = cfg["slug"]
            date_str = cfg["date"]
        export_pdfs(company_slug=slug, date_str=date_str, all_files=args.all)
    elif args.command == "run":
        run_end_to_end(args.config)



if __name__ == "__main__":
    main()
