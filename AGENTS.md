# WebResume & ATS Career Engine Guidelines

This repository (`resume-template`) contains an interactive bilingual web resume, ATS-optimized portfolio, and automated job application engine driven by a central Single Source of Truth (`config/profile.json` / `config/profile.example.json`).

---

## 1. Single Source of Truth (SSOT) & Invariants

All candidate details, invariants, search parameters, and platform links are configured centrally in:
- `config/profile.example.json` (authoritative schema & defaults)
- `config/profile.json` (active configuration instance)

- **Candidate Identity**: `candidate.name`, `candidate.title_en`, `candidate.title_de`, address, phone, email, and portfolio links. Pre-configured personas:
  * **Fullstack Software Engineer**: `config/profile.example.json` (Alex Morgan, Berlin)
  * **Cloud DevOps & Platform Engineer**: `config/profile.devops.example.json` (Elena Becker, Munich)
  * **UI/UX & Product Designer**: `config/profile.designer.example.json` (Julian Richter, Hamburg)
  * **Banking, Finance & Controlling**: `config/profile.finance.example.json` (Clara Lindemann, Frankfurt)
  * **Mechanical & Energy Systems Engineering**: `config/profile.engineering.example.json` (Stefan Kramer, Stuttgart)
- **Target Compensation (*Gehaltsvorstellung*)**: Governed by `invariants.target_salary_phrase_de` (e.g. `65.000 Euro brutto im Jahr`).
- **Notice Period (*Kündigungsfrist*)**: Governed by `invariants.notice_period_de` (e.g. `dreimonatigen Kündigungsfrist zum Monatsende, im Einvernehmen gern auch kurzfristiger`).
- **Portfolio & Link Rules**:
  - Cover letters dynamically link to `candidate.links_url`.
  - Prohibited domains: Enforced via `candidate.prohibited_domains` (e.g. `resume.example.com`).
- **Technical Formatting (Spaced Terms Only)**:
  - Do **NOT** use hyphens (`-`) for compound technical terms and job titles.
  - Correct: `REST APIs`, `CI/CD Pipelines`, `MCP Tools`, `KI Agenten`, `Fullstack Entwickler`, `Fullstack Engineer`, `Cloud Architekturen`, `Figma Design`, `n8n Workflows`.
  - Incorrect: `REST-APIs`, `CI/CD-Pipelines`, `Fullstack-Entwickler`, `Full-Stack Engineer`.
- **UI Design & Formatting**:
  - **Never use emojis** in resume HTML, cover letters, or PDF exports. Use clean Lucide icons or SVG vectors.
- **Zero Scratch Scripts Mandate**:
  - Never write ad-hoc scratch scripts (`test_*.py`, `inspect_*.py`).
  - All generation, DOM validation, cover letter rendering, and PDF compilation MUST be executed via the unified engine: `jobs/engine.py`.
- **No Visual Screenshots**:
  - Do NOT capture visual screenshots or render pages to PNG. All testing is conducted programmatically via DOM inspection and PDF text validation.

---

## 2. Technical Stack & Architecture

| Layer | Technologies | Role / Notes |
| :--- | :--- | :--- |
| **SSOT Configuration** | JSON (`config/profile.json`) | Single source of truth for candidate details, invariants, search preferences, and platforms |
| **Master Resume** | HTML5, CSS3, Tailwind CSS, Lucide Icons | `index.html` — Semantic, bilingual (`data-lang-en`, `data-lang-de`), Schema.org JSON-LD |
| **Styling & Print** | Vanilla CSS (`style.css`), `@media print` | A4 standard page sizing, clean page breaks, selectable ATS text |
| **Automation Engine** | Python 3, Chromium headless | `jobs/engine.py` — Unified CLI runner for tailoring, cover letters, roles, and PDFs |
| **Export Formats** | Clean HTML, DIN-5008 PDF | Client-side export via `html2canvas` / `jsPDF`, headless server-side generation via `jobs/engine.py` |

---

## 3. Directory Layout & Workflow Structure

```text
resume-template/
├── config/
│   ├── profile.example.json     # Authoritative SSOT schema & template defaults
│   └── profile.json             # Active user profile (copied from example)
├── index.html                   # Master bilingual web resume (source of truth for base profile)
├── style.css                    # Typography, theme variables, print & PDF stylesheets
├── alex-morgan-profile.webp     # Default candidate profile portrait
├── download.html                # PDF download landing helper
├── daily-job-search-workflow.md # Authoritative daily job intake & tailoring SOP
├── daily-job-search-links.md    # Generated German tech job search queries & platform links
└── jobs/
    ├── engine.py                # Unified CLI runner for tailoring, cover letters, and PDFs
    ├── job_matches.md           # Opportunity tracking matrix & score dashboard
    ├── configs/                 # Job configuration JSONs (YYYY-MM-DD_[company].json)
    ├── job_descriptions/        # Raw job descriptions & requirements
    ├── cover_letters/           # Generated DIN-5008 HTML & PDF cover letters
    ├── resumes/                 # Generated tailored HTML & PDF resumes
    ├── roles/                   # Pre-validated canonical role archetypes (*.json)
    └── prompts/                 # AI system prompts (Cover letters, STAR prep, Tailoring)
```

---

## 4. Automation Engine Commands

Run all automation from the repository root:

```bash
# 1. Run full application package generation (config -> resume HTML -> cover letter HTML -> PDFs)
python jobs/engine.py run --config jobs/configs/YYYY-MM-DD_[company_slug].json

# 2. Build and validate all canonical role resumes
python jobs/engine.py build-roles

# 3. Render daily job search links dashboard from profile SSOT
python jobs/engine.py build-links

# 4. Initialize a new skeleton application config for a target company
python jobs/engine.py init-config --slug [company_slug] --date YYYY-MM-DD --role fullstack_laravel

# 5. Validate master resume DOM structure
python jobs/engine.py validate-resume --file index.html
```
