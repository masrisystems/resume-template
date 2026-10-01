---
name: daily-job-workflow
description: Standardized, zero-token-waste automation skill for discovering jobs, qualifying matches, generating tailored resumes, crafting DIN-5008 cover letters, and compiling PDFs via jobs/engine.py.
tags:
  - career
  - job-search
  - web-resume
  - automation
---

# Daily Job Discovery & Application Automation Skill

This skill enforces a token-efficient, zero-scratch-script execution of the daily job search and application preparation workflow.

## Strict Operational Mandates

1. **NEVER Write Scratch Scripts:**
   - Do NOT write temporary Python scripts (such as `test_resumes.py`, `inspect_*.py`, `test_cls.py`) in `scratch/`.
   - All resume generation, HTML DOM validation, DIN-5008 cover letter templating, n-gram overlap checks, and headless PDF exports are built into the unified CLI engine: `jobs/engine.py`.
2. **Declare Applications via JSON Config or Canonical Roles:**
   - Initialize and declare each application's content in a concise JSON configuration file under `jobs/configs/YYYY-MM-DD_<company_slug>.json` using `python jobs/engine.py init-config`.
   - Prefer mapping to pre-validated canonical roles (`role_profile: "[role_id]"`) from `jobs/roles/`.
3. **Core Invariants (Defined in `config/profile.json`):**
   - **Target Compensation:** Sourced from `invariants.target_salary_phrase_de` (e.g. *"65.000 Euro brutto im Jahr"*).
   - **Notice Period:** Sourced from `invariants.notice_period_de` (e.g. *"dreimonatige Kündigungsfrist zum Monatsende, im Einvernehmen gern auch kurzfristiger"*). NEVER claim "ab sofort".
   - **Portfolio Proof:** Sourced from `candidate.links_url` (e.g. `https://links.example.com`).
   - **Domain Prohibition:** Sourced from `candidate.prohibited_domains` (e.g. generic resume URLs).
   - **Spaced Compound Words:** No hyphens in technical terms (`REST APIs`, `CI/CD Pipelines`, `MCP Tools`, `Fullstack Entwickler`, `Cloud Architekturen`).
   - **Anti-AI Formatting:** Under 300 words, zero em dashes, zero semicolons, straight quotes only, burstiness range >= 20 words with short punchy fragments (<= 5 words).

---

## The Standardized 5-Step Workflow

### Step 1: Discover & Qualify (Target: 2 Jobs/Day)
1. Read `jobs/job_matches.md` to deduplicate against all existing companies and URLs.
2. Search and verify active vacancies scoring >= 9.0/10 (Required 70%, Preferred 30%).
3. Preserve raw job descriptions in `jobs/job_descriptions/<company_slug>.txt`.

### Step 2: Initialize & Fill Application Configs
Initialize a declarative configuration JSON using the engine:
```powershell
python jobs/engine.py init-config --slug <company_slug> --date YYYY-MM-DD --role <role_id>
```
This produces `jobs/configs/YYYY-MM-DD_<company_slug>.json`:
```json
{
  "slug": "company_slug",
  "date": "YYYY-MM-DD",
  "role_profile": "fullstack_laravel",
  "cover_letter": {
    "company_clean": "Company Name GmbH",
    "sender_title": "Senior Fullstack Entwickler · PHP 8, Laravel & Vue.js",
    "recipient_company": "<Company Name & Dept>",
    "recipient_person": "<Hiring Contact / Recruiter Name & Team>",
    "recipient_address": "<Street · ZIP City>",
    "subject_line": "Bewerbung als <Job Title>",
    "salutation": "Sehr geehrte(r) <Salutation>,",
    "paragraphs": [
      "<Paragraph 1: Company mission hook, role match, philosophy>",
      "<Paragraph 2: 5+ years experience, stack, APIs, testing, CI/CD, AI>",
      "<Paragraph 3: Target salary from profile, notice period from profile, portfolio link from profile>"
    ]
  }
}
```

*Note on DOM Parity:* `skills_frontend` must have exactly 2 items, `skills_backend` 4 items, `skills_devops` 5 items, and `skills_secondary` 2 items to ensure 100% DOM tag sequence parity with `index.html`.

### Step 3: Run the Unified Automation Engine
Execute the entire generation, validation, and PDF export in a single command:
```powershell
python jobs/engine.py run --config jobs/configs/YYYY-MM-DD_<company_slug>.json
```

This single command automatically:
1. Compiles `jobs/resumes/<company_slug>.html` from `index.html`.
2. Validates DOM parity, script/style byte-identity, banned hyphen patterns, and prohibited domains.
3. Compiles `jobs/cover_letters/YYYY-MM-DD_<company_slug>.html` with DIN-5008 CSS.
4. Validates cover letter length (<300 words), invariants, 8-word JD overlap, and 12-word cross-letter overlap.
5. Launches headless Chrome/Edge to generate:
   - `jobs/resumes/<company_slug>.pdf`
   - `jobs/resumes/YYYY-MM-DD_<company_slug>.pdf`
   - `jobs/cover_letters/YYYY-MM-DD_<company_slug>.pdf`

### Step 4: Update Opportunity Tracker
Append the new entries to `jobs/job_matches.md` with status `🟡 [Ready to Submit]`.

### Step 5: Master Resume Maintenance Review & Morning Action Brief
1. Review `index.html` against documented work in `What I worked.md` and today's market demand.
2. Save suggestions (or no-change assessment) in `jobs/resume_suggestions/YYYY-MM-DD.md`.
3. Output the concise Morning Action Brief with clickable links to the generated HTML and PDF files.
