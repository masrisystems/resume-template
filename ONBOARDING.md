# WebResume & ATS Career Engine: Onboarding Guide

Welcome to **WebResume & ATS Career Engine**! This guide walks you through setting up your personal resume, configuring your contractual invariants, generating your first DIN-5008 cover letter, and starting your daily application routine.

---

## 🚀 The 5-Minute Fast Track: Choose Your Setup Method

You can set up your profile in one of two ways:
1. **The AI Assistant Method (Recommended):** Use our onboarding prompt to ingest your existing resume (or answer 7 guided questions) and automatically generate your configuration.
2. **The Persona Template Method:** Pick one of 5 pre-configured industry personas and edit the JSON directly.

---

## Method 1: The AI Assistant Setup (Fastest & Automated)

We provide a dedicated onboarding prompt located at [`jobs/prompts/onboarding_profile_prompt.txt`](jobs/prompts/onboarding_profile_prompt.txt).

### Step 1: Copy the AI Prompt
Open your preferred LLM (ChatGPT, Claude, Gemini, or local Ollama) and paste the system prompt from [`jobs/prompts/onboarding_profile_prompt.txt`](jobs/prompts/onboarding_profile_prompt.txt):

```text
# Role & Persona: Senior Technical Recruiter & ATS Systems Engineer
# Mission: Onboard the candidate to WebResume & ATS Career Engine.
# Input: Either paste your existing resume / LinkedIn profile text, OR say "Interview me".
```

### Step 2: Feed Your Data
- **If you have a resume or LinkedIn profile:** Simply paste the text or upload your PDF/Markdown resume right after the prompt. The AI will extract your details, rewrite your accomplishments into quantified STAR bullet points, translate them into German and English, and output a complete `config/profile.json`.
- **If you don't have a resume ready:** Say *"Interview me"*. The AI will ask you 7 simple questions:
  1. Full name, contact info, city, and portfolio/social links.
  2. Target role and title (DE/EN).
  3. Core tech stack (top 6–10 technologies).
  4. Work history (last 2–3 jobs and key achievements).
  5. Measurable metrics & impact (latency, revenue, team size, scale).
  6. Target salary and notice period (contractual invariants).
  7. Search preferences (city, commute radius, remote/hybrid).

### Step 3: Save Your Configuration
Copy the generated JSON code block and save it to:
```bash
config/profile.json
```

---

## Method 2: The Persona Template Setup (Manual)

If you prefer to configure manually, we ship 5 pre-validated industry profiles:

| Persona | Config File | Target Field |
| :--- | :--- | :--- |
| **Fullstack Software Engineer** | `config/profile.example.json` | Web, Cloud, AI & Fullstack |
| **Cloud DevOps & Platform Engineer** | `config/profile.devops.example.json` | Kubernetes, CI/CD, AWS/GCP |
| **UI/UX & Product Designer** | `config/profile.designer.example.json` | Design Systems, Figma, Research |
| **Banking, Finance & Controlling** | `config/profile.finance.example.json` | Financial Modeling, SAP, IFRS |
| **Mechanical & Energy Systems** | `config/profile.engineering.example.json` | CAD, Thermodynamics, CleanTech |

Copy your chosen persona to activate it:
```bash
cp config/profile.example.json config/profile.json
```
Open `config/profile.json` in your editor and adjust your contact information, target salary, and experience.

---

## 🛠️ Step 2: Build & Verify Your Career Hub

Once `config/profile.json` is saved, run the automation engine from the project root:

```bash
# 1. Render your personalized job discovery dashboard:
python jobs/engine.py build-links

# 2. Compile pre-validated canonical role resumes (HTML & PDF):
python jobs/engine.py build-roles

# 3. Validate your master resume DOM structure:
python jobs/engine.py validate-resume --file index.html
```

Open `index.html` in your browser. You will see:
- Your interactive bilingual web resume (switch between EN and DE with 1 click).
- Working print and PDF export buttons.
- The 24 specialized career agent skills and AI prompt library.

---

## 🎯 Step 3: Tailoring Your First Job Application (Daily Routine)

When you find an interesting job posting, generate a tailored application package in 15 minutes:

### 1. Initialize a Target Job Config
```bash
python jobs/engine.py init-config --slug acme_corp --date 2026-10-01 --role fullstack_laravel
```
This generates a skeleton configuration at `jobs/configs/2026-10-01_acme_corp.json`.

### 2. Save the Job Description
Paste the employer's job description into:
```text
jobs/job_descriptions/acme_corp.txt
```

### 3. Generate Your Tailored Cover Letter & Resume
Use our production prompts from `jobs/prompts/`:
- **For DIN-5008 Cover Letter:** [`jobs/prompts/cover_letter_prompt.txt`](jobs/prompts/cover_letter_prompt.txt)
- **For ATS Resume Tailoring:** [`jobs/prompts/resume_prompt.txt`](jobs/prompts/resume_prompt.txt)

Paste the output into your job configuration file `jobs/configs/2026-10-01_acme_corp.json`.

### 4. Compile the End-to-End Package
Run the unified CLI runner:
```bash
python jobs/engine.py run --config jobs/configs/2026-10-01_acme_corp.json
```

The engine automatically validates and outputs:
- **Tailored Resume:** `jobs/resumes/acme_corp.html` and `jobs/resumes/acme_corp.pdf`
- **DIN-5008 Cover Letter:** `jobs/cover_letters/2026-10-01_acme_corp.html` and `jobs/cover_letters/2026-10-01_acme_corp.pdf`

Both documents are now ready to upload directly to Personio, Workday, Greenhouse, or email to the recruiter.

---

## 📌 Critical Guidelines & Invariants

1. **Single Source of Truth:** Never hardcode your phone number, email, or salary in individual files. Always edit `config/profile.json`.
2. **Technical Spelling (Spaced Terms Only):**
   - Correct: `REST APIs`, `CI/CD Pipelines`, `MCP Tools`, `Fullstack Entwickler`, `Vue.js`.
   - Incorrect: `REST-APIs`, `CI/CD-Pipelines`, `Fullstack-Entwickler`.
3. **Zero Emojis in Resumes & Cover Letters:** Emojis trigger ATS parsing errors and look unprofessional on German DIN-5008 letters. Use clean SVG vector icons or Lucide icons.
4. **Contractual Invariants:** Your notice period (`invariants.notice_period_de`) and gross annual salary expectation (`invariants.target_salary_phrase_de`) are automatically injected into every cover letter generated by the engine.

---

## ❓ Need Help?

- **Daily Job Search Routine:** See [`daily-job-search-workflow.md`](daily-job-search-workflow.md)
- **Search Query Matrix:** See [`daily-job-search-links.md`](daily-job-search-links.md)
- **Promotion & Distribution:** See [`docs/where-to-share.md`](docs/where-to-share.md)
