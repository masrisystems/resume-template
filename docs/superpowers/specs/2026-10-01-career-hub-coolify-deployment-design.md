# Design Specification: Career Hub & Coolify Deployment (`career.masrisystems.com`)

**Date**: 2026-10-01  
**Target Domain**: `career.masrisystems.com`  
**Host & Orchestration**: Coolify (Alpine Caddy Container)  
**Status**: Approved & Ready for Implementation  

---

## 1. Executive Summary & Product Vision

`career.masrisystems.com` serves as an open-source Career Hub and interactive showcase for the Masri Systems WebResume & ATS Career Engine. It delivers three core offerings to job seekers, engineers, and hiring teams:
1. **Interactive Bilingual Web Resume**: ATS-optimized, DIN-5008-aligned master resume template featuring instant German/English toggle, A4 print/PDF export, ATS plain-text mode, and multi-archetype persona switching (Fullstack, DevOps, Designer, Finance, Engineering).
2. **AI Prompt Library**: Sourced directly from battle-tested production prompts (`jobs/prompts/`), enabling 1-click clipboard copy of structured prompts for Cover Letters, ATS Resume Tailoring, STAR Behavioral Interview Prep, Boolean Job Search Queries, and Daily Job Workflow.
3. **Workflow & 24 Agent Skills Catalog**: A structured breakdown of the automated daily job application routine and interactive catalog of the 24 specialized career agent skills (`skills/*`).
4. **Starter Kit Download**: One-click download of the complete standalone starter kit bundle (`resume-template-starter.zip`), allowing users to clone, configure, and automate their job search locally.

---

## 2. Aesthetic System: Airtable Editorial Dialect

The user interface follows Airtable's editorial design system: a white canvas floor, near-black ink typography (`#181d26`), generous vertical whitespace (`96px`), high-voltage full-bleed signature cards, and restrained corner radii.

### 2.1 Color Tokens
* **Base & Ink**:
  * `--color-primary` / `--color-ink`: `#181d26` (Primary CTA background, h1/h2 headings, signature dark surfaces)
  * `--color-primary-active`: `#0d1218` (Pressed button state)
  * `--color-canvas`: `#ffffff` (Page floor)
  * `--color-surface-soft`: `#f8fafc` (Featured cards and tab containers)
  * `--color-surface-strong`: `#e0e2e6` (Light CTA banner near footer)
  * `--color-hairline`: `#dddddd` (1px subtle borders, dividers, secondary button outlines)
  * `--color-body`: `#333840` (Running copy)
  * `--color-muted`: `#41454d` (Captions, metadata, breadcrumbs)
  * `--color-on-primary` / `--color-on-dark`: `#ffffff` (Text on dark and signature cards)
* **Signature Voltage Surfaces**:
  * `--color-sig-coral`: `#aa2d00` (Full-bleed high-impact callout card)
  * `--color-sig-forest`: `#0a2e0e` (Deep green signature surface for ATS engine highlights)
  * `--color-sig-cream`: `#f5e9d4` (Soft beige callout band for skills and workflows)
  * `--color-sig-peach`: `#fcab79` (Demo-card prompt surface)
  * `--color-sig-mint`: `#a8d8c4` (Demo-card prompt surface)
  * `--color-sig-yellow`: `#f4d35e` (Demo-card prompt surface)
  * `--color-sig-mustard`: `#d9a441` (Demo-card prompt surface)
* **Semantic & Links**:
  * `--color-link`: `#1b61c9` (Inline hyperlinks only; never primary buttons)
  * `--color-info`: `#254fad` / `--color-info-border`: `#458fff` (Focus rings and active badges)
  * `--color-success`: `#006400` / `--color-success-border`: `#39bf45` (Toast and copy confirmation)

### 2.2 Typography & Hierarchy
* **Font Family**: `Inter Display, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
* **Weights & Scales**:
  * Display Headlines (`h1` / `h2`): `font-weight: 400` (32px to 40px), using scale and color contrast instead of heavy bold weights.
  * Subtitles & Button Labels: `font-weight: 500` (16px to 20px).
  * Body Text: `font-weight: 400` (14px, line-height 1.45).
* **Typographic Rules**: Zero emojis anywhere in the UI. Precision Lucide SVG vector icons exclusively. Spaced compound technical terms (`REST APIs`, `CI/CD Pipelines`, `MCP Tools`, `Fullstack Entwickler`).

### 2.3 Spacing, Borders & Section Rhythm
* **Section Padding**: Universal `96px` (`padding-top: 6rem; padding-bottom: 6rem`) between major editorial bands.
* **Border Radii**:
  * `{rounded.lg}` (`12px`): Primary CTAs, large signature cards (`coral`, `forest`, `dark`).
  * `{rounded.md}` (`10px`): Content cards, demo-grid prompt cards, cream callout bands.
  * `{rounded.sm}` (`6px`): Search filters, text inputs, code copy blocks.
  * `{rounded.full}` (`9999px`): Circular icon buttons, persona switcher pills.
* **Section Rhythm**:
  1. Pinned 64px White Top Nav
  2. White Canvas Hero Band (96px whitespace, title, subtitle, dual CTA buttons)
  3. Signature Coral Card (`#aa2d00`) — The Open Source Career Engine
  4. AI Prompt Library — Demo cards on pastel surfaces with 1-click clipboard copy
  5. Signature Cream Callout Band (`#f5e9d4`) — 24 Agent Skills & Daily Search Routine
  6. Live Interactive Resume Template — Embedded showcase with persona pills and print/PDF export
  7. Light Gray CTA Banner (`#e0e2e6`) — Download Starter Kit
  8. White Canvas Editorial Footer

---

## 3. Component Architecture & Interactions

### 3.1 Technology Stack
* **Markup**: Semantic HTML5 (`index.html`)
* **Styling**: Vanilla CSS (`style.css`), utilizing CSS variables for design tokens.
* **Icons**: Lucide Icons (SVG vector elements, zero emojis).
* **Scripting**: Pure Vanilla JavaScript (ES6+), zero frontend frameworks, zero npm runtime dependencies.
* **Packaging**: Static pre-compiled ZIP (`resume-template-starter.zip`).

### 3.2 Key Interactive Components

#### Top Navigation (`top-nav`)
* Fixed 64px white bar with 1px hairline border (`#dddddd`).
* Left: Brand mark `WebResume & Career Engine` with Masri Systems tag.
* Center: Navigation links to `#prompts`, `#workflows`, `#resume`, `#download`.
* Right: Language toggle (`EN` / `DE`), link to Portfolio (`https://links.masrisystems.com`), and primary near-black CTA button ("Download Kit").

#### AI Prompt Library (`#prompts`)
* Grid of 5 production prompt cards:
  1. **DIN-5008 Cover Letter Prompt** (`jobs/prompts/cover_letter_prompt.txt`)
  2. **ATS Resume Tailoring Prompt** (`jobs/prompts/resume_prompt.txt`)
  3. **STAR Method Interview Prep** (`jobs/prompts/interview_prompt.txt`)
  4. **Job Search & Query Generator** (`jobs/prompts/find_jobs_prompt.txt`)
  5. **Daily Job Workflow Routine** (`jobs/prompts/daily_job_workflow_prompt.md`)
* Each card includes:
  * Prompt title, description, and recommended LLMs (Claude 3.7, GPT-4o, Gemini 2.0 Pro).
  * Collapsible prompt body with highlighted placeholders (`{{COMPANY}}`, `{{JOB_TITLE}}`, `{{JOB_DESCRIPTION}}`).
  * 1-Click Copy button with clipboard API (`navigator.clipboard.writeText`) and feedback toast ("Prompt copied to clipboard!").

#### Workflows & 24 Agent Skills Directory (`#workflows`)
* Visual 4-stage pipeline: *Discover* → *Ingest & Score* → *Tailor & Generate* → *Validate ATS & Export*.
* Searchable and filterable directory of the 24 career agent skills grouped by domain:
  * **Resume Optimization**: ATS Optimizer, Tailor, Bullet Writer, Quantifier, Formatter, Section Builder.
  * **Letters & Applications**: Cover Letter Generator, Application Form Filler, Portfolio Case Study Writer.
  * **Career Transitions**: Executive Resume Writer, Career Changer Translator, Academic CV Builder, Creative Portfolio.
  * **Interviews & Offers**: Interview Coach, Interview Prep Generator, Salary Negotiation Prep, Offer Comparison Analyzer.
  * **Job Market Intelligence**: Daily Job Workflow, Job Description Analyzer, LinkedIn Profile Optimizer, Reference List Builder.

#### Live Resume Showcase (`#resume`)
* Embedded preview of the master bilingual web resume (defaults to Alex Morgan / Fullstack).
* **Archetype Selector Pills**:
  * Fullstack Software Engineer (`profile.example.json`)
  * Cloud DevOps & Platform Engineer (`profile.devops.example.json`)
  * UI/UX & Product Designer (`profile.designer.example.json`)
  * Banking, Finance & Controlling (`profile.finance.example.json`)
  * Mechanical & Energy Systems Engineering (`profile.engineering.example.json`)
* **ATS Mode Toggle**: Strips styling down to pure accessible text for automated parser verification.
* **Print & PDF Isolation**: `@media print` rules isolate `#resume-paper`, hiding all hub navigation, hero bands, prompt cards, and footers when printing or compiling PDFs via headless Chromium.

#### Download & Quickstart Section (`#download`)
* Prominent download card for `resume-template-starter.zip`.
* 3-step Quickstart guide:
  1. `git clone` or unzip the starter kit.
  2. Copy and customize `config/profile.example.json` to `config/profile.json`.
  3. Run `python jobs/engine.py run --config ...` to generate DIN-5008 cover letters and tailored resumes.

---

## 4. Coolify Deployment & Server Architecture

### 4.1 Web Server & Container Configuration
* **Base Image**: `caddy:2-alpine` (official, lightweight, security-audited Alpine image, <35MB).
* **`Dockerfile`**:
  * Multi-stage build or direct Alpine stage copying web assets into `/srv`.
  * Generates/bundles `resume-template-starter.zip` into `/srv/download/`.
  * Runs unprivileged Caddy daemon on port 80.
* **`Caddyfile`**:
  * Binds to `:80`.
  * Compression: `encode gzip zstd`.
  * Static file server: `file_server`.
  * Single Page routing fallback: `try_files {path} /index.html`.
  * HTTP Security Headers:
    * `X-Content-Type-Options: nosniff`
    * `X-Frame-Options: SAMEORIGIN`
    * `Referrer-Policy: strict-origin-when-cross-origin`
    * `Permissions-Policy: geolocation=(), camera=(), microphone=()`
  * Cache headers:
    * HTML: `Cache-Control: no-cache, must-revalidate`
    * Static CSS/JS/Images/ZIP: `Cache-Control: public, max-age=31536000, immutable`

### 4.2 Coolify Orchestration Files
* **`docker-compose.yml`**:
  * Service: `career-hub`
  * Restart: `unless-stopped`
  * Ports: `80:80`
  * Healthcheck: `wget -q --spider http://localhost:80/ || exit 1`
  * Labels configured for Coolify Traefik reverse proxy routing to `career.masrisystems.com` with automated Let's Encrypt TLS certificate.
* **`.dockerignore`**:
  * Excludes `.git`, `.venv`, `__pycache__`, local scratch scripts, and temporary PDF output directories to ensure lean and instantaneous container builds.

---

## 5. Verification & Quality Gates

1. **DOM Structure & Accessibility Verification**:
   * All navigation anchors (`#prompts`, `#workflows`, `#resume`, `#download`) exist and resolve properly.
   * Clipboard copy interaction works seamlessly without console errors.
   * Zero emojis across all rendered HTML and CSS.
   * Semantic heading hierarchy (`h1` -> `h2` -> `h3`).
2. **Print & PDF Layout Validation**:
   * Running `jobs/engine.py validate-resume` verifies clean DOM structure.
   * Native print preview / PDF rendering outputs strictly the A4 resume without landing page chrome.
3. **Coolify Container Healthcheck**:
   * Local container build (`docker build -t career-hub .`) succeeds.
   * Container serves HTTP 200 on `/`, `/download/resume-template-starter.zip`, and static assets.
