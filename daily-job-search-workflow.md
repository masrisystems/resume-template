---
title: "Daily Job Discovery & Application Preparation Workflow"
description: "Daily automated search, qualification ranking, tailoring, cover-letter HTML generation, and master-resume maintenance."
tags:
  - workflow
  - career
  - job-search
  - web-resume
created: 2026-09-01
updated: 2026-09-30
status: active
---

# Daily Job Discovery & Application Preparation Workflow

## Objective
Discover, qualify, and prepare complete, factual application packages (canonical Role-Archetype HTML resume, DIN-5008 print-ready HTML cover letter, plus high-fidelity PDF exports of both the resume and cover letter ready for portal upload) for two target software engineering roles daily (target: 2 qualifying jobs per day scoring >= 9.0/10), and evaluate daily master-resume and role-archetype improvements against documented work notes.

Use the installed skills in this order: `daily-job-workflow`, `job-description-analyzer`, `resume-tailor`, `resume-bullet-writer`, `cover-letter-generator`, and `humanize`. Treat `index.html`, canonical role definitions (`jobs/roles/*.json`), and private work notes as factual sources; never invent experience, skills, metrics, dates, titles, salary evidence, vacancy status, or distance.

## Scope & Safety Rules
- **Workspace Scope:** Work in the resume project root (`resume-template/`).
- **Single Source of Truth (SSOT):** All candidate details, invariants, search preferences, and platform query templates are defined in `config/profile.json` (fallback: `config/profile.example.json`). Never hardcode candidate data.
- **Zero Scratch Scripts Mandate:** Never write temporary scratch scripts (`test_*.py`, `inspect_*.py`). All resume generation, DOM validation, cover letter templating, originality overlap checking, and headless PDF exports MUST be executed exclusively via the unified engine: `python jobs/engine.py run --config jobs/configs/YYYY-MM-DD_[company_slug].json`.
- **Canonical Role Archetypes Architecture:** Instead of re-generating bespoke, slightly divergent resumes per company, the candidate maintains a discrete catalog of 5 pre-validated, high-impact Role Archetypes under `jobs/roles/`:
  1. `fullstack_laravel`: Senior Fullstack Entwickler · PHP 8, Laravel & Vue.js (VILT Stack, Inertia, REST APIs, MySQL, Docker, CI/CD)
  2. `fullstack_node_react`: Senior Full Stack Developer · TypeScript, React, Next.js & Node.js (Express, GraphQL/REST, PostgreSQL, Docker)
  3. `shopware_php_backend`: Senior E-Commerce & Backend Entwickler · Shopware 6, PHP 8 & Symfony (DAL, Plugins, Pimcore/ERP, Redis, MySQL)
  4. `frontend_ui_architect`: Senior Frontend Entwickler & UI Architekt · Vue.js, React & TypeScript (Nuxt, Next.js, Tailwind CSS, Core Web Vitals 95+)
  5. `ai_product_engineer`: Senior AI & Fullstack Product Engineer · TypeScript, Python & Agentic Workflows (Claude Code, Cursor, MCP Tools, RAG, LLM Integration)
  The engine compiles and validates all roles simultaneously via `python jobs/engine.py build-roles` to `jobs/roles/html/` and `jobs/roles/pdf/`. Daily application configs simply declare `"role_profile": "[role_id]"` rather than repeating 50 lines of duplicate resume schemas.
- **Factual Evidence:** Read authentic work logs and documented achievements. Never invent experience, skills, metrics, dates, titles, salary evidence, vacancy status, or distance.
- **Candidate Availability & Notice Period:** The candidate's notice period is defined in `config/profile.json` under `invariants.notice_period_de` (e.g. *dreimonatige Kündigungsfrist zum Monatsende, im Einvernehmen gern auch kurzfristiger*). NEVER claim "ab sofort" or "sofort verfügbar" in resumes, cover letters, or action briefs. If availability is addressed in a cover letter, phrase it professionally using the invariant from `config/profile.json`. In the Morning Action Brief checklist, guide the user using this invariant or the calculated earliest start date.
- **Salary Expectation (*Gehaltsvorstellung*):** Target salary is defined in `config/profile.json` under `invariants.target_salary_phrase_de` (e.g. *65.000 Euro brutto im Jahr*). Always state this exact invariant whenever salary expectations are stated or requested in cover letters, questionnaires, or tracker targets.
- **Portfolio Link in Cover Letters:** Always use the URL configured in `config/profile.json` under `candidate.links_url` (e.g. `https://links.example.com`).
- **Domain Prohibition:** Strictly NEVER mention or link to prohibited domains configured in `config/profile.json` under `candidate.prohibited_domains`. Because every resume is individually tailored per job vacancy, directing recruiters to a generic resume URL exposes the generic master resume which differs from their tailored version.
- **No Hyphenated Compounds Rule:** Do NOT use hyphens (`-`) in compound technical terms or titles in resumes, cover letters, and trackers. Use spaced compound words: e.g., `REST APIs` (not `REST-APIs`), `Figma Design` (not `Figma-Design`), `CI/CD Pipelines` (not `CI/CD-Pipelines`), `n8n Workflows` (not `n8n-Workflows`), `MCP Tools` (not `MCP-Tools`), `KI Agenten` (not `KI-Agenten`), `Fullstack Entwickler` (not `Fullstack-Entwickler`), `Fullstack Engineer` (not `Full-Stack Engineer`), `Cloud Architekturen` (not `Cloud-Architekturen`).
- **PDF & HTML Deliverables:** Application assets are delivered in clean, print-ready HTML AND high-fidelity PDF exports ready for portal submission:
  * Tailored Resume: `jobs/resumes/[company_slug].html` and `jobs/resumes/[company_slug].pdf` (plus date-stamped copy `jobs/resumes/YYYY-MM-DD_[company_slug].pdf`).
  * DIN-5008 Cover Letter: `jobs/cover_letters/YYYY-MM-DD_[company_slug].html` and `jobs/cover_letters/YYYY-MM-DD_[company_slug].pdf` (e.g. `2026-10-01_example_tech.pdf`).
  * Automated compilation & validation: Executed in one step via `python jobs/engine.py run --config jobs/configs/YYYY-MM-DD_[company_slug].json`.
  * Markdown (`.md`) duplicate files and PNG visual preview files remain strictly prohibited.
- **No Visual Image Rendering:** Visual image rendering (rendering pages to PNG/JPG, capturing screenshots via headless Chrome/Puppeteer/DevTools, or creating image preview artifacts) is completely unnecessary and strictly prohibited across all stages of the workflow. Do NOT render pages to PNG, do NOT take visual screenshots, and do NOT generate visual preview artifacts. All verification is performed programmatically via DOM inspection, HTML syntax validation, and PDF page/text structure inspection.
- **Git & Master Resume Protection:** Inspect git status first and preserve unrelated or overlapping edits. Do not commit, push, deploy, submit an application, contact an employer, create an account, or change the master `index.html`.
- **Atomic Packages:** Complete each selected job as an atomic package. Do not mark it submitted unless every required artifact and validation succeeds.
- **Directory Safety:** Create directories only when required by a qualifying result.


---

## Execution Pipeline

### 1. Dedupe Before Searching
- Read `jobs/job_matches.md` first and parse every existing row.
- Build case-insensitive normalized sets of company names and canonical URLs (removing fragments, tracking parameters, and trailing slashes).
- Exclude a candidate if either its company or any job/application URL is already present. A new role at an already-listed company is still a duplicate.
- Never rewrite, reformat, or “correct” existing tracker rows.

### 2. Search & Verify Active Postings
- Search current German and English postings for:
  a) Full-stack web development and frontend engineering roles across any modern frontend framework (Vue.js / Nuxt, React / Next.js, Angular, Svelte, TypeScript, modern JavaScript, Tailwind CSS);
  b) Modern PHP / Laravel (VILT / Inertia.js, Filament, APIs), Symfony, or enterprise web application development;
  c) Closely related full-stack software engineering and web-development roles.
- **Direct Quick-Links & Saved Search Queries:** Consult [[daily-job-search-links.md]] (automatically generated via `python jobs/engine.py build-links` from `config/profile.json`) for direct, pre-configured search URLs.
- **Curated Tech & Investment Discovery Sources:**
  To discover scaling tech employers, venture-backed startups, and recently funded technology companies actively hiring:
  1. **Techstars Portfolio Search:** [techstars.com/portfolio#search-portfolio](https://www.techstars.com/portfolio#search-portfolio) — Explore Techstars portfolio tech companies, filter by geography and technology sector to uncover fast-growing tech teams.
  2. **High-Tech Gründerfonds (HTGF) Newsroom:** [htgf.de/newsroom](https://www.htgf.de/newsroom/) — Monitor recent seed and growth investments, venture deals, and portfolio updates across the tech ecosystem to track funded companies scaling headcount.
  3. **Messen.de IT & Career Fairs Directory:** [messen.de/de/de/in/deutschland/regionen-uebersicht](https://www.messen.de/de/de/in/deutschland/regionen-uebersicht) — Search trade fairs, developer conferences, and recruiting events across your region to connect with hiring tech companies 1-on-1.
- **Priority 1:** Commuter region and primary locations configured in `config/profile.json` under `search_preferences.locations` (default: Berlin commuter region up to ~40 km).
- **Priority 2:** Roles explicitly allowing 100% remote work from the candidate's residence country. Do not treat “remote-friendly,” occasional home office, EU-wide remote, or an unclear location policy as 100% remote.
- **Verification Gate:** Use aggregators for discovery only. Before selection, open an official company careers page or direct ATS/application page and verify that the exact title, company, location/work arrangement, and application action are currently visible. A search snippet, generic careers page, cached page, or aggregator alone is not proof that a vacancy is active.
- Prefer fresh postings when a reliable publication date is visible. Record “date not stated” rather than guessing.
- For regional roles, report a sourced approximate road distance from the configured home address when available; otherwise report “distance not independently verified.” Do not invent a distance.

### 3. Analyze & Rank Before Generating
- Extract required, preferred, and soft-skill requirements from the verified full description.
- Calculate qualification match exactly as defined by the `job-description-analyzer` skill: required skills 70%, preferred skills 30%, then divide the weighted percentage by 10 for a 0-10 score. Keep the unrounded calculation, display one decimal, and list evidence for each matched requirement.
- **Dealbreaker Gate:** A missing explicit dealbreaker is a critical gap (disqualify). Do not select candidates with critical gaps. Check language requirements against `candidate.languages` in `config/profile.json`.
- **Role Archetype Mapping:** Classify the vacancy into the best-matching canonical role archetype (`fullstack_laravel`, `fullstack_node_react`, `shopware_php_backend`, `frontend_ui_architect`, `ai_product_engineer`).
- Rank qualifying candidates by: qualification score, Priority 1 over Priority 2, direct stack overlap, source quality, then freshness.
- **Two-Job Daily Target:** Target and prepare complete application packages for two qualifying jobs daily whenever two or more reach >= 9.0/10. Search thoroughly across configured commuter regions and verified remote vacancies to reach the two-job daily goal. Do not stop at one when a second qualifying vacancy can be found. If an exhaustive search yields only one qualifying role, prepare that package completely and report the second best near-match along with its honest blockers. If none qualify, create no application assets and make no tracker changes; report the best near-match and its honest blockers.
- Extract the five most important ATS keywords only when they truthfully match documented experience. Missing keywords remain gaps and must never be added as claimed skills.

### 4. Preserve Description & Salary Evidence
- For each selected job, save the complete plain-text posting to `jobs/job_descriptions/[company_slug].txt`. Include a short header with exact role, company, source URL, official application URL, retrieval date in Europe/Berlin, visible publication date or “not stated,” and work arrangement; then include the full description without model paraphrasing.
- Research compensation using current public evidence. Prefer the exact company and comparable role on kununu/Glassdoor. Record source URL, retrieval date, sample/context when visible, and whether the number is an employer-specific salary, a company-wide role average, or a broader market benchmark.
- Never label a general market estimate as a “kununu estimate.” If no defensible range is available, write “No reliable public salary range found.”

### 5. Create Resume (Automated via jobs/engine.py)
- Do NOT write Python scripts or write ad-hoc 50-line custom resume blocks in config JSONs.
- Initialize the application config using the unified engine:
  ```powershell
  python jobs/engine.py init-config --slug [company_slug] --date YYYY-MM-DD --role [role_id]
  ```
- This produces a lean config under `jobs/configs/YYYY-MM-DD_[company_slug].json` declaring `"role_profile": "[role_id]"`.
- The engine automatically resolves the canonical role archetype from `jobs/roles/[role_id].json` and strictly enforces:
  * DOM tag sequence and attribute parity with `index.html` (frontend: 2 `<li>`, backend: 4 `<li>`, devops: 5 `<li>`, secondary: 2 `<li>`).
  * 0 mentions of prohibited domains from `config/profile.json`.
  * 0 banned hyphenated terms (`REST APIs`, `CI/CD Pipelines`, `MCP Tools`, `Fullstack Entwickler`).
  * Byte-identical `<script>` and `<style>` blocks.
- *(Backwards compatibility & flexibility)*: If an exceptional vacancy requires a specific single-bullet tweak, an optional `"resume"` override object can be provided in the config, but canonical role mapping is the standard.
- **Validation Gate:** Executed automatically during compilation via `python jobs/engine.py run --config ...` (or standalone: `python jobs/engine.py validate-resume --slug [slug]`).

### 6. Create Cover Letter HTML & Generate PDFs (Automated via jobs/engine.py)
- Define the cover letter content (recipient, subject, 3 paragraphs) inside the same config: `jobs/configs/YYYY-MM-DD_[company_slug].json`.
- **Invariants Built Into Engine (sourced dynamically from `config/profile.json`):**
  * Fixed target salary: `invariants.target_salary_phrase_de`.
  * Contractual notice period: `invariants.notice_period_de`.
  * Portfolio evidence link: `candidate.links_url`.
  * Word count: Strictly below 300 words.
  * Humanize anti-AI rules: Zero em dashes, zero semicolons, straight quotes only, burstiness range >= 20 words with short punchy fragments (<= 5 words).
  * Deterministic overlap checks: 0 8-word sequence overlap with `jobs/job_descriptions/[slug].txt` and 0 12-word cross-letter body overlap across `jobs/cover_letters/*.html`.
- **One-Command Compilation & Verification:**
  Run the unified engine:
  ```powershell
  python jobs/engine.py run --config jobs/configs/YYYY-MM-DD_[company_slug].json
  ```
  This command builds the HTML resume, validates it, builds the DIN-5008 HTML cover letter, validates it against all invariants and n-gram overlap gates, and generates both resume and cover letter PDFs via headless Chrome.
- **No Visual Rendering:** Do NOT render pages to PNG or take visual screenshots. All verification is performed programmatically by `jobs/engine.py`.

### 7. Update Tracker
- Re-check `jobs/job_matches.md` immediately before writing to avoid duplicates introduced during the run.
- Append exactly one escaped Markdown table row per fully successful package, using the existing column order:
  `Job Title | Company Name | Location | Job Type | Status | Match Score (0-10) | Match Justification | Skill Gap | Salary Range | Apply Link`
- **Direct Submission Status:** Set Status directly to submitted with the execution date: `🔵 [Submitted: YYYY-MM-DD]` (e.g. `🔵 [Submitted: 2026-09-30]`). Applications are submitted immediately upon package generation as part of the daily workflow; never leave them as pending or ready. For subsequent pipeline stages, retain the historical submission date context (e.g. `🟣 [Screening Invited (Submitted: YYYY-MM-DD)]`, `⚪ [Position Closed (Submitted: YYYY-MM-DD)]`).
- Use the verified direct official application URL, not a generic careers or aggregator URL.
- Keep Match Justification to one evidence-based sentence; list at most two honest gaps; make the salary source label explicit.
- Preserve the table structure and all existing content.

### 8. Master Resume & Role Catalog Maintenance Review
- Run this stage every day after completing the job-search and application-package work, even when no job reaches 9.0/10.
- Read the current master `index.html`, canonical role definitions (`jobs/roles/*.json`), and documented project work logs and achievements (e.g. `What I worked.md`). Use `jobs/job_matches.md` only to identify recurring market demand; never turn a job-description requirement into a claimed skill.
- Look for durable, documented evidence that is genuinely stronger than something already in the master resume or role profiles: shipped systems, architecture ownership, measurable performance or reliability improvements, enterprise scale, leadership, business impact, or a repeatedly requested technology already demonstrated in the Work notes.
- Apply `resume-tailor` and `resume-bullet-writer`, but override any suggestion to estimate metrics. Use only exact numbers documented in `index.html` or the private Work notes. If a result has no verified number, write a concise qualitative result.
- Suggest no more than three edits; prefer one or two. Make no suggestion merely to fill the section.
- **Strict No-Bloat Budget:**
  * add no section;
  * add no bullet;
  * keep the total bullet count unchanged;
  * keep the proposed total resume word count at or below the current total;
  * replace or tighten an existing bullet before considering any new information;
  * preserve employer names, titles, dates, education, contact facts, and HTML structure.
- A proposal qualifies only when the new evidence is specific, source-traceable, relevant to the recurring target roles, and clearly more valuable than the exact text it would replace. If it is merely different, narrower, repetitive, outdated, or relevant to only one vacancy, do not recommend it for the master resume.
- Do not edit `index.html` or any tailored resume automatically. Produce suggestions for user approval only.
- For every suggestion provide:
  1. Priority: Replace now, Tighten, or Hold for targeted resumes only.
  2. Target section and the exact current text to replace.
  3. Proposed replacement text.
  4. Exact supporting Work file path and heading or line reference.
  5. Target file(s): `index.html` and/or specific `jobs/roles/[role_id].json`.
  6. Why the replacement is stronger for the target market.
  7. Bullet-count delta and word-count delta; both must show no growth overall.
- If no evidence clears the bar, state “No master-resume change recommended today.”
- When one or more suggestions qualify, save the same concise proposal to `jobs/resume_suggestions/YYYY-MM-DD.md` so it can be reviewed later. Do not create a file for a no-change result.
- When an update is approved by the user and applied, run `python jobs/engine.py build-roles` to refresh all canonical role PDFs at once.

### 9. Return Morning Action Brief
- For each successful package show role, company, mapped Role Archetype, location/work arrangement plus sourced distance or verification note, salary evidence and source type, match score, direct official Apply link, and clickable absolute local links to all generated application assets:
  * **Role Archetype:** `fullstack_laravel` (or matching canonical role key)
  * **Resume (HTML):** `file:///.../jobs/resumes/[company_slug].html`
  * **Resume (PDF):** `file:///.../jobs/resumes/[company_slug].pdf` (or `YYYY-MM-DD_[company_slug].pdf`)
  * **Canonical Role PDF:** `file:///.../jobs/roles/pdf/[Candidate_Name]_Lebenslauf_[role_id].pdf` (e.g. `Alex_Morgan_Lebenslauf_[role_id].pdf`)
  * **DIN-5008 Cover Letter (HTML):** `file:///.../jobs/cover_letters/YYYY-MM-DD_[company_slug].html`
  * **DIN-5008 Cover Letter (PDF):** `file:///.../jobs/cover_letters/YYYY-MM-DD_[company_slug].pdf` (e.g. `2026-10-01_example_tech.pdf`)
  * **Preserved Job Description:** `file:///.../jobs/job_descriptions/[company_slug].txt`
- Also state the top five ATS keywords, the most important gap, any manual check still required, and a compact cover-letter and PDF QA line: humanization/paraphrasing pass, number of overlap sources checked, spelling/grammar pass, HTML print readiness, and automated PDF export verification (1-page DIN-5008 cover letter PDF and multi-page tailored resume PDF).
- If nothing qualified, say “No new >= 9.0/10 verified match today,” summarize search coverage and the top blocker, and do not imply that assets were created.
- Include a Human-in-the-Loop Pre-Submission Checklist with exact portal form guidance for availability (derived from `config/profile.json` invariant: *Kündigungsfrist zum Monatsende, im Einvernehmen gern auch kurzfristiger* / calculated earliest start date).
- After the job brief, include a separate “Resume Maintenance Suggestions” section containing the approved-format proposals from stage 8, or the explicit no-change statement.
- When a dated suggestion file was created, include a clickable absolute local link to it.
- Clearly distinguish verified facts from estimates. Do not claim an application was submitted or that a suggested master-resume edit was applied.
