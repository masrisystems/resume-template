# 🌐 Interactive Web Resume & ATS Career Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE.txt)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python)](https://python.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com)

> **Modern, responsive, bilingual web resume and automated job application engine.** Designed for high performance, ATS readability, dual PDF export, and SSOT-driven customization.

---

## 🌟 Key Features

- **🎯 Single Source of Truth (`config/profile.json`)**: Configure candidate contact details, target compensation, notice period, search preferences, and search platform queries in one central place.
- **🌐 Dynamic Bilingual Switcher (DE / EN)**: Instant seamless client-side toggle between German and English without page reloads.
- **🌓 Dark & Light Theme**: Persistent system-aware theme toggle with smooth transitions and Tailwind CSS styling.
- **📄 Dual PDF Export Strategy**:
  - **Client-side Direct Export**: One-click PDF generation via `html2canvas` and `jsPDF`.
  - **Headless Chrome / Edge Export**: High-fidelity, print-ready PDF export via `jobs/engine.py` using standard A4 sizing.
- **🤖 Unified Application Engine (`jobs/engine.py`)**:
  - Automatically compiles and validates tailored HTML and PDF resumes.
  - Automatically generates DIN-5008 compliant German cover letters with strict quality and invariant checks.
  - Automatically renders daily job discovery link dashboards (`daily-job-search-links.md`).
- **🏆 Pre-Validated Canonical Roles**: Includes 5 pre-configured, high-impact role archetypes in `jobs/roles/` for rapid tailoring.

---

## 🚀 Quick Start

> 💡 **New here? Check out the [Onboarding Guide (ONBOARDING.md)](ONBOARDING.md)** for a guided 5-minute setup using our interactive AI onboarding prompt (paste your existing resume or answer 7 quick questions).

### 1. Clone & Setup Configuration
Choose from one of the pre-configured profile templates:
- **Fullstack Software Engineer:** `config/profile.example.json` (Alex Morgan, Berlin)
- **Cloud DevOps & Platform Engineer:** `config/profile.devops.example.json` (Elena Becker, Munich)
- **UI/UX & Product Designer:** `config/profile.designer.example.json` (Julian Richter, Hamburg)
- **Banking, Finance & Controlling:** `config/profile.finance.example.json` (Clara Lindemann, Frankfurt)
- **Mechanical & Energy Systems Engineering:** `config/profile.engineering.example.json` (Stefan Kramer, Stuttgart)

Copy your preferred profile template to create your active configuration:
```bash
cp config/profile.example.json config/profile.json
```
Edit `config/profile.json` with your personal details, target salary, notice period, and preferred search locations (or let the [AI Onboarding Prompt](jobs/prompts/onboarding_profile_prompt.txt) generate it automatically from your old resume).
You can also run any engine command directly against a specific profile using `--profile [path]`.

### 2. Render Search Links Dashboard
Generate your personalized job discovery dashboard from your profile:
```bash
python jobs/engine.py build-links
```

### 3. Build Canonical Role Resumes
Compile all 5 pre-validated role archetypes to HTML and PDF:
```bash
python jobs/engine.py build-roles
```

### 4. Apply to a Target Job
Scaffold a new application config for a target company:
```bash
python jobs/engine.py init-config --slug example_tech --date 2026-10-01 --role fullstack_laravel
```
Edit `jobs/configs/2026-10-01_example_tech.json` and run the end-to-end pipeline:
```bash
python jobs/engine.py run --config jobs/configs/2026-10-01_example_tech.json
```
The engine will generate, validate, and export:
- Tailored Resume: `jobs/resumes/example_tech.html` & `example_tech.pdf`
- DIN-5008 Cover Letter: `jobs/cover_letters/2026-10-01_example_tech.html` & `2026-10-01_example_tech.pdf`

---

## 📂 Project Structure

```text
resume-template/
├── config/
│   ├── profile.example.json     # Authoritative SSOT schema & defaults
│   └── profile.json             # Active candidate profile
├── index.html                   # Master bilingual web resume (source of truth)
├── style.css                    # Typography, print & PDF stylesheets
├── alex-morgan-profile.webp     # Default candidate profile portrait
├── download.html                # Dedicated download landing helper
├── daily-job-search-links.md    # Generated job search queries & platform links
├── daily-job-search-workflow.md # Daily application intake & tailoring SOP
└── jobs/
    ├── engine.py                # Unified CLI runner for tailoring, cover letters, and PDFs
    ├── job_matches.md           # Opportunity tracker & match scoring matrix
    ├── configs/                 # Job configuration JSONs (YYYY-MM-DD_[company].json)
    ├── job_descriptions/        # Raw job postings & requirements
    ├── cover_letters/           # Generated DIN-5008 HTML & PDF cover letters
    ├── resumes/                 # Generated tailored HTML & PDF resumes
    ├── roles/                   # Pre-validated canonical role archetypes (*.json)
    └── prompts/                 # AI system prompts (Resume, Cover Letter, Prep, Search)
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE.txt).
