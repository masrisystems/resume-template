import json
import re
from html.parser import HTMLParser
from pathlib import Path
from .config import (
    MASTER_INDEX,
    RESUMES_DIR,
    ROLES_DIR,
    ROLES_HTML_DIR,
    ROLES_PDF_DIR,
    load_profile,
    sync_stylesheets,
)
from .pdf import find_browser, html_to_pdf


class DOMStructureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.non_lang_attrs = []
        self.interactive_ids = set()

    def handle_starttag(self, tag, attrs):
        self.tags.append(("start", tag))
        filtered_attrs = []
        attrs_dict = dict(attrs)
        for k, v in attrs:
            if k in ("data-lang-en", "data-lang-de"):
                continue
            if tag == "meta" and k == "content" and ("og:title" in attrs_dict.values() or "twitter:title" in attrs_dict.values()):
                continue
            if k == "id":
                self.interactive_ids.add(v)
            filtered_attrs.append((k, v))
        self.non_lang_attrs.append((tag, tuple(sorted(filtered_attrs))))

    def handle_endtag(self, tag):
        self.tags.append(("end", tag))


def validate_resume_file(tailored_path: Path, master_path: Path = MASTER_INDEX) -> bool:
    tailored_path = Path(tailored_path)
    master_path = Path(master_path)
    if not tailored_path.exists():
        raise FileNotFoundError(f"Tailored resume file not found: {tailored_path}")
    if not master_path.exists():
        raise FileNotFoundError(f"Master index file not found: {master_path}")

    master_html = master_path.read_text(encoding="utf-8")
    tailored_html = tailored_path.read_text(encoding="utf-8")

    profile = load_profile()
    prohibited = profile.get("candidate", {}).get("prohibited_domains", [])
    for dom in prohibited:
        if dom in tailored_html:
            raise ValueError(f"Prohibited domain '{dom}' found in {tailored_path}")

    banned_hyphens = [
        r"\bREST-APIs?\b",
        r"\bFigma-Designs?\b",
        r"\bCI/CD-Pipelines?\b",
        r"\bn8n-Workflows?\b",
        r"\bMCP-Tools?\b",
        r"\bMCP-Servers?\b",
        r"\bKI-Agenten?\b",
        r"\bFullstack-Entwickler\b",
        r"\bFull-Stack-Entwickler\b",
        r"\bFull-Stack Developer\b",
        r"\bFull-Stack Engineer\b",
        r"\bCloud-Architekturen?\b",
    ]
    for pat in banned_hyphens:
        m = re.search(pat, tailored_html, re.IGNORECASE)
        if m:
            raise ValueError(f"Found banned hyphenated technical term '{m.group(0)}' in {tailored_path}")

    for block_type in ["script", "style"]:
        m_blocks = re.findall(rf"<{block_type}.*?</{block_type}>", master_html, re.DOTALL)
        t_blocks = re.findall(rf"<{block_type}.*?</{block_type}>", tailored_html, re.DOTALL)
        if len(m_blocks) != len(t_blocks):
            raise ValueError(
                f"{block_type.capitalize()} block count mismatch: master={len(m_blocks)}, tailored={len(t_blocks)}"
            )
        for idx, (ms, ts) in enumerate(zip(m_blocks, t_blocks)):
            if ms != ts:
                raise ValueError(f"{block_type.capitalize()} block {idx} differs between master and {tailored_path}")

    m_parser, t_parser = DOMStructureParser(), DOMStructureParser()
    m_parser.feed(master_html)
    t_parser.feed(tailored_html)

    if m_parser.tags != t_parser.tags:
        raise ValueError(f"DOM tag sequence does not match master in {tailored_path}")
    if m_parser.non_lang_attrs != t_parser.non_lang_attrs:
        raise ValueError(f"Non-language attributes do not match master in {tailored_path}")

    expected_ids = {
        "resumeContent",
        "header",
        "work-experience",
        "current-role",
        "brainkets-role",
        "side-projects-role",
        "technical-skills",
        "education",
        "academic-achievements",
        "languages",
        "footer",
        "theme-toggle",
        "downloadPdf",
    }
    missing_ids = expected_ids - t_parser.interactive_ids
    if missing_ids:
        raise ValueError(f"Missing required interactive IDs in {tailored_path}: {missing_ids}")

    print(f"[OK] Resume Validation PASSED: {tailored_path.name}")
    return True


def get_resume_config(config: dict) -> dict:
    if "role_profile" in config:
        role_id = config["role_profile"]
        role_file = ROLES_DIR / f"{role_id}.json"
        if not role_file.exists():
            raise FileNotFoundError(f"Role profile not found: {role_file}")
        role_data = json.loads(role_file.read_text(encoding="utf-8"))
        if "resume" in config and isinstance(config["resume"], dict):
            merged = dict(role_data)
            merged.update(config["resume"])
            return merged
        return role_data
    if "resume" in config:
        return config["resume"]
    raise KeyError("Config must contain either 'role_profile' or 'resume'")


def generate_resume_html(res_cfg: dict, master_html: str = None) -> str:
    c = master_html if master_html is not None else MASTER_INDEX.read_text(encoding="utf-8")
    cand_name = load_profile().get("candidate", {}).get("name", "Alex Morgan")

    title = res_cfg.get("title", f"{cand_name} | {res_cfg.get('subtitle_de', 'Fullstack Developer')} — Resume").replace(
        "{candidate_name}", cand_name
    )
    og_title = res_cfg.get("og_title", title.split(" — ")[0]).replace("{candidate_name}", cand_name)
    twitter_title = res_cfg.get("twitter_title", og_title).replace("{candidate_name}", cand_name)

    c = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", c, count=1)
    c = re.sub(r'<meta property="og:title" content=".*?" />', f'<meta property="og:title" content="{og_title}" />', c, count=1)
    c = re.sub(r'<meta name="twitter:title" content=".*?" />', f'<meta name="twitter:title" content="{twitter_title}" />', c, count=1)

    sub_re = r'          <p class="mt-1 font-semibold text-\[#a9583e\] dark:text-\[#e8a55a\]".*?</p>'
    if not re.search(sub_re, c, re.DOTALL):
        raise ValueError("Could not find subtitle block in master index.html")
    c = re.sub(
        sub_re,
        f'          <p class="mt-1 font-semibold text-[#a9583e] dark:text-[#e8a55a]"\n            data-lang-en="{res_cfg["subtitle_en"]}"\n            data-lang-de="{res_cfg["subtitle_de"]}">\n            {res_cfg["subtitle_en"]}\n          </p>',
        c,
        count=1,
        flags=re.DOTALL,
    )

    sum_re = r'          <p class="mt-2 max-w-2xl text-sm text-gray-700 dark:text-gray-300".*?</p>'
    if not re.search(sum_re, c, re.DOTALL):
        raise ValueError("Could not find summary block in master index.html")
    c = re.sub(
        sum_re,
        f'          <p class="mt-2 max-w-2xl text-sm text-gray-700 dark:text-gray-300"\n            data-lang-en="{res_cfg["summary_en"]}"\n            data-lang-de="{res_cfg["summary_de"]}">\n            {res_cfg["summary_en"]}\n          </p>',
        c,
        count=1,
        flags=re.DOTALL,
    )

    def make_skills(h_en, h_de, h_disp, items):
        lis = "\n".join(f"            <li>{it}</li>" for it in items)
        return (
            f'        <div>\n'
            f'          <h4 class="font-semibold" data-lang-en="{h_en}" data-lang-de="{h_de}">\n'
            f'            {h_disp}\n'
            f'          </h4>\n'
            f'          <ul class="list-disc ml-5">\n{lis}\n          </ul>\n'
            f'        </div>'
        )

    sections = [
        (
            "skills_frontend",
            2,
            r'        <div>\s*<h4 class="font-semibold" data-lang-en="Frontend \(Primary\)" data-lang-de="Frontend \(Primär\)">.*?</ul>\s*</div>',
        ),
        (
            "skills_backend",
            4,
            r'        <div>\s*<h4 class="font-semibold" data-lang-en="Backend \(Primary\)" data-lang-de="Backend \(Primär\)">.*?</ul>\s*</div>',
        ),
        (
            "skills_devops",
            5,
            r'        <div>\s*<h4 class="font-semibold" data-lang-en="DevOps & Tools" data-lang-de="DevOps & Werkzeuge">.*?</ul>\s*</div>',
        ),
        (
            "skills_secondary",
            2,
            r'        <div>\s*<h4 class="font-semibold" data-lang-en="Secondary / Previous Stack" data-lang-de="Sekundär-Stack &amp; Frühere Technologien">.*?</ul>\s*</div>',
        ),
    ]

    for key, expected_count, regex in sections:
        cfg = res_cfg[key]
        if len(cfg["items"]) != expected_count:
            raise ValueError(f"{key} must have exactly {expected_count} items for DOM parity, got {len(cfg['items'])}")
        block = make_skills(cfg["heading_en"], cfg["heading_de"], cfg["heading_display"], cfg["items"])
        c = re.sub(regex, block, c, count=1, flags=re.DOTALL)

    replacements = {
        "Shopware 6.6": "Shopware",
        "Laravel 12 / Vue 3 / Inertia": "Laravel / Vue.js / Inertia",
        "Vue.js 3": "Vue.js",
        "Vue 3": "Vue.js",
    }
    for old, new in replacements.items():
        c = c.replace(old, new)
    return c


def build_resume_from_config(config_path: Path) -> Path:
    sync_stylesheets()
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    c = generate_resume_html(get_resume_config(config))

    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RESUMES_DIR / f"{config['slug']}.html"
    out_file.write_text(c, encoding="utf-8")
    print(f"[OK] Wrote Tailored Resume: {out_file}")
    validate_resume_file(out_file)
    return out_file


def build_role(role_path_or_id) -> tuple[Path, Path]:
    sync_stylesheets()
    role_file = role_path_or_id if isinstance(role_path_or_id, Path) else ROLES_DIR / f"{role_path_or_id}.json"
    if not role_file.exists():
        raise FileNotFoundError(f"Role config not found: {role_file}")

    cand_name = load_profile().get("candidate", {}).get("name", "Alex Morgan")
    cand_slug = re.sub(r"[\s\-/]", "_", cand_name).replace(".", "")
    role_cfg = json.loads(role_file.read_text(encoding="utf-8"))
    role_id = role_cfg.get("role_id", role_file.stem)

    ROLES_HTML_DIR.mkdir(parents=True, exist_ok=True)
    out_html = ROLES_HTML_DIR / f"{role_id}.html"
    out_html.write_text(generate_resume_html(role_cfg), encoding="utf-8")
    print(f"[OK] Wrote Role HTML: {out_html.name}")
    validate_resume_file(out_html)

    ROLES_PDF_DIR.mkdir(parents=True, exist_ok=True)
    out_pdf = ROLES_PDF_DIR / f"{cand_slug}_Lebenslauf_{role_id}.pdf"
    html_to_pdf(find_browser(), out_html, out_pdf)
    print(f"[OK] Wrote Role PDF: {out_pdf.name}")
    return out_html, out_pdf


def build_all_roles(specific_role: str = None) -> list:
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
