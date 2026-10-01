import glob
import json
import re
from pathlib import Path
from .config import COVER_LETTERS_DIR, JOB_DESCRIPTIONS_DIR, load_profile

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


def format_german_date(date_str: str, location: str = "Berlin") -> str:
    months = {
        "01": "Januar",
        "02": "Februar",
        "03": "März",
        "04": "April",
        "05": "Mai",
        "06": "Juni",
        "07": "Juli",
        "08": "August",
        "09": "September",
        "10": "Oktober",
        "11": "November",
        "12": "Dezember",
    }
    parts = date_str.split("-")
    if len(parts) == 3:
        year, month, day = parts
        day_int = int(day)
        month_de = months.get(month, month)
        return f"{location}, {day_int}. {month_de} {year}"
    return f"{location}, {date_str}"


def get_ngrams(tokens: list, n: int) -> set:
    return set(" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1))


def validate_cover_letter_file(cl_path: Path, jd_path: Path = None) -> bool:
    cl_path = Path(cl_path)
    if not cl_path.exists():
        raise FileNotFoundError(f"Cover letter file not found: {cl_path}")

    profile = load_profile()
    cand = profile.get("candidate", {})
    invariants = profile.get("invariants", {})

    content = cl_path.read_text(encoding="utf-8")
    paras = re.findall(r'<div class="paragraph">(.*?)</div>', content, re.DOTALL)
    if not paras:
        raise ValueError(f'No <div class="paragraph"> elements found in {cl_path}')

    body_text = " ".join(re.sub(r"<[^>]+>", "", p) for p in paras)
    words = body_text.split()

    if len(words) >= 300:
        raise ValueError(f"Word count {len(words)} >= 300 limit in {cl_path}")

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

    if "{{" in content or "}}" in content:
        raise ValueError(f"Unrendered double curly braces found in {cl_path}")

    for req_css in ["@page {", "size: A4;", "body {", ".header-row {", ".footer-note {"]:
        if req_css not in content:
            raise ValueError(f"Required CSS rule '{req_css}' missing in {cl_path}")

    if "—" in body_text or "–" in body_text:
        raise ValueError(f"Em/en dashes found in cover letter body {cl_path.name}. Use hyphens or rephrase.")
    if ";" in body_text:
        raise ValueError(f"Semicolon found in cover letter body {cl_path.name}. Simplify sentence structure.")
    if any(q in body_text for q in ["“", "”", "„", "«", "»"]):
        raise ValueError(f"Curved quotes found in {cl_path.name}. Use straight quotes only.")

    banned_fillers = [
        r"\bdelve\b",
        r"\bleverage\b",
        r"\butilize\b",
        r"\brobust\b",
        r"\bcomprehensive\b",
        r"\bstreamline\b",
        r"\bfurthermore\b",
        r"\bmoreover\b",
        r"\bit is important to note\b",
    ]
    for b in banned_fillers:
        if re.search(b, body_text, re.IGNORECASE):
            raise ValueError(f"Banned buzzword pattern '{b}' detected in {cl_path.name}")

    sentences = [s.strip() for s in re.split(r"[.!?]+", body_text) if s.strip()]
    sentence_lengths = [len(s.split()) for s in sentences]
    if sentence_lengths:
        variance_range = max(sentence_lengths) - min(sentence_lengths)
        has_punchy = any(l <= 5 for l in sentence_lengths)
        if variance_range < 20:
            print(f"[WARN] Sentence length range ({variance_range} words) is below recommended 20-word floor in {cl_path.name}")
        if not has_punchy:
            print(f"[WARN] No punchy sentence (<= 5 words) found in {cl_path.name}")

    tokens = re.sub(r"[^\w\s]", " ", body_text).lower().split()
    cl_8grams = get_ngrams(tokens, 8)

    target_jd = (
        Path(jd_path)
        if jd_path
        else JOB_DESCRIPTIONS_DIR / f"{re.sub(r'^\d{4}-\d{2}-\d{2}_', '', cl_path.stem)}.txt"
    )
    if target_jd.exists():
        jd_tokens = re.sub(r"[^\w\s]", " ", target_jd.read_text(encoding="utf-8")).lower().split()
        overlap = cl_8grams.intersection(get_ngrams(jd_tokens, 8))
        if overlap:
            raise ValueError(f"8-word sequence overlap with job description in {cl_path}: {overlap}")

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
        overlap = cl_12grams.intersection(ng2)
        if overlap:
            raise ValueError(f"12-word cover letter body overlap between {cl_path.name} and {Path(other).name}: {overlap}")

    print(f"[OK] Cover Letter Validation PASSED: {cl_path.name} ({len(words)} words)")
    return True


def build_cover_letter_from_config(config_path: Path) -> Path:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    slug, date_str, cl_cfg = config["slug"], config["date"], config["cover_letter"]
    profile = load_profile()
    cand = profile.get("candidate", {})
    inv = profile.get("invariants", {})

    cand_name = cand.get("name", "Alex Morgan")
    cand_addr = f"{cand.get('address_street', 'Musterstraße 123')} · {cand.get('address_city', '10115 Berlin')}"
    cand_phone = cand.get("phone", "+49 151 12345678")
    cand_email = cand.get("email", "alex.morgan@example.com")
    cand_links = cand.get("links_url", cand.get("portfolio_url", "https://links.example.com"))
    cand_links_display = re.sub(r"^https?://", "", cand_links).rstrip("/")
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
        "{paragraphs_html}": paragraphs_html,
    }
    html = DIN_5008_TEMPLATE
    for k, v in replacements.items():
        html = html.replace(k, v)

    COVER_LETTERS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = COVER_LETTERS_DIR / f"{date_str}_{slug}.html"
    out_file.write_text(html, encoding="utf-8")
    print(f"[OK] Wrote Cover Letter HTML: {out_file}")
    validate_cover_letter_file(out_file)
    return out_file
