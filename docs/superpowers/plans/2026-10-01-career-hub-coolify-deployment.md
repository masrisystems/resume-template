# Career Hub & Coolify Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and deploy an open-source Career Hub (`career.masrisystems.com`) on Coolify, featuring an ATS-optimized bilingual web resume, an interactive AI prompt library with 1-click copy, a 24-agent skills catalog, a downloadable starter kit, and lightweight Alpine Caddy containerization following Airtable's editorial design system.

**Architecture:** Pure Vanilla HTML5, modern CSS3 adhering to Airtable editorial design tokens (white canvas, ink typography `#181d26`, 96px vertical rhythm, signature coral/forest/cream surface cards, zero emojis), and Vanilla JS for 1-click copy and persona switching. Containerized via Alpine Caddy (`caddy:2-alpine`) with HTTP/2, compression, and security headers for one-click Coolify hosting.

**Tech Stack:** Semantic HTML5, Vanilla CSS (`style.css`), Vanilla JavaScript (ES6+), Lucide Icons (SVG), Caddy 2 Alpine, Docker, Docker Compose, Python (build packaging & validation).

---

## File Structure & Responsibilities

| File | Responsibility |
| :--- | :--- |
| `style.css` | Airtable editorial design tokens, typography, vertical rhythm (96px), signature cards, buttons, responsive rules, and print isolation |
| `index.html` | Unified Career Hub page: TopNav, HeroBand, SignatureCoralCard, PromptLibrary, SkillsCatalog, LiveResumeShowcase, DownloadCTA, and Editorial Footer |
| `hub.js` | Vanilla JS interactions: 1-click clipboard copy with toast notifications, persona archetype switcher, smooth scroll, and ATS text toggle |
| `scripts/bundle_starter_kit.py` | Build script creating the clean `download/resume-template-starter.zip` package containing templates, configs, prompts, skills, and CLI engine |
| `Dockerfile` | Alpine Caddy container image packaging static assets, starter zip, and Caddy server |
| `Caddyfile` | Web server configuration: port 80, gzip/zstd compression, security headers, asset caching, SPA fallback |
| `docker-compose.yml` | Coolify deployment specification with health checks and restart policies |
| `.dockerignore` | Build context exclusions to ensure minimal image size (<35MB) and zero secret leakage |
| `tests/test_career_hub.py` | Automated test suite verifying DOM anchors, prompt copy payloads, skills catalog counts, zero-emoji policy, and print isolation |

---

### Task 1: Test Suite & DOM Verification Infrastructure

**Files:**
- Create: `tests/test_career_hub.py`

- [ ] **Step 1: Write the failing test for Career Hub structure & invariants**

```python
import os
import re
from bs4 import BeautifulSoup

def test_hub_structure_and_invariants():
    index_path = "index.html"
    assert os.path.exists(index_path), "index.html must exist"
    
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. Zero emojis invariant check
    emoji_pattern = re.compile(
        "[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\U0001f300-\U0001f9ff]",
        flags=re.UNICODE
    )
    matches = emoji_pattern.findall(content)
    assert len(matches) == 0, f"Found prohibited emojis in index.html: {set(matches)}"
    
    # 2. Key section anchors exist
    soup = BeautifulSoup(content, "html.parser")
    required_ids = ["hero", "prompts", "workflows", "resume", "download"]
    for req_id in required_ids:
        assert soup.find(id=req_id) is not None, f"Missing section #{req_id} in index.html"
    
    # 3. Prompt library contains 5 production prompt cards
    prompt_cards = soup.select(".prompt-card")
    assert len(prompt_cards) >= 5, f"Expected at least 5 prompt cards, found {len(prompt_cards)}"
    
    # 4. Print isolation check: resume-paper exists and hub navigation has no-print
    resume_paper = soup.find(id="resume-paper")
    assert resume_paper is not None, "Missing #resume-paper container"
    top_nav = soup.find(id="top-nav")
    assert top_nav is not None and "no-print" in top_nav.get("class", []), "Top nav must have 'no-print' class"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_career_hub.py -v`  
Expected: FAIL (missing section anchors and prompt cards)

- [ ] **Step 3: Commit test file**

```bash
git add tests/test_career_hub.py
git commit -m "test: add DOM and invariant verification tests for career hub"
```

---

### Task 2: Airtable Editorial Design System Stylesheet (`style.css`)

**Files:**
- Modify: `style.css`

- [ ] **Step 1: Add Airtable editorial CSS variables, typography, and section tokens to `style.css`**

Add CSS custom properties for:
- Canvas, Ink, Surface Soft, Surface Strong, Hairline borders
- Signature surfaces: Coral (`#aa2d00`), Forest (`#0a2e0e`), Cream (`#f5e9d4`), Peach, Mint, Yellow
- Typography scale: Haas/Inter Display at 400 regular display weights, 500 button weights
- Universal 96px vertical section padding (`--spacing-section: 96px`)
- Button hierarchy: near-black primary CTA (`12px` rounded-lg) + hairline outline secondary CTA
- Print stylesheet rules isolating `#resume-paper` and hiding `.no-print` elements (`#top-nav`, `#hero`, `#prompts`, `#workflows`, `#download`, `footer`)

- [ ] **Step 2: Verify existing print & ATS styling integrity**

Run: `python jobs/engine.py validate-resume --file index.html`  
Expected: PASS with 0 DOM errors

- [ ] **Step 3: Commit stylesheet updates**

```bash
git add style.css
git commit -m "style: implement airtable editorial design tokens, signature cards, and print isolation"
```

---

### Task 3: Interactive Hub Logic & 1-Click Copy (`hub.js`)

**Files:**
- Create: `hub.js`

- [ ] **Step 1: Write Vanilla JS for prompt copying, toast notifications, and persona switching**

Implement:
1. `copyPrompt(buttonElement)`: extracts prompt text from `data-prompt` or sibling element, calls `navigator.clipboard.writeText`, displays floating toast notification (`#hub-toast`).
2. `switchPersona(personaKey)`: updates resume preview title, summary, and skills based on pre-loaded persona archetypes (Fullstack, DevOps, Designer, Finance, Engineering).
3. `toggleAtsMode()`: toggles plain-text ATS view on the live resume preview.
4. Smooth anchor scroll event listeners.

- [ ] **Step 2: Create unit test in `tests/test_career_hub.py` verifying `hub.js` syntax & exports**

Add test checking that `hub.js` defines required handler functions without syntax errors.  
Run: `python -m pytest tests/test_career_hub.py -v`  
Expected: PASS

- [ ] **Step 3: Commit `hub.js`**

```bash
git add hub.js tests/test_career_hub.py
git commit -m "feat(ui): add vanilla JS interaction layer for prompt copying and persona switching"
```

---

### Task 4: Career Hub Markup & Section Integration (`index.html`)

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Add editorial Top Navigation bar (`#top-nav`)**
  - 64px white bar, hairline border, brand mark "WebResume & Career Engine", navigation links, language toggle, and primary "Download Kit" button. Mark with `no-print`.

- [ ] **Step 2: Add Hero Band (`#hero`)**
  - White canvas, 96px vertical padding, Haas/Inter display typography (h1 weight 400), value proposition for the open-source career engine, dual button pair ("Explore Prompts", "Preview Template"). Mark with `no-print`.

- [ ] **Step 3: Add Signature Coral Card**
  - `#aa2d00` full-bleed card introducing the Dual Engine: ATS-optimized interactive resume + LLM prompt engineering. Mark with `no-print`.

- [ ] **Step 4: Add AI Prompt Library Section (`#prompts`)**
  - Demo cards on pastel surfaces (`mint`, `peach`, `yellow`, `cream`, `canvas`) embedding the 5 battle-tested prompts from `jobs/prompts/` with 1-click copy buttons. Mark with `no-print`.

- [ ] **Step 5: Add Workflows & Skills Catalog Section (`#workflows`)**
  - Cream callout band (`#f5e9d4`) detailing the 4-stage daily routine and categorized directory of the 24 career agent skills. Mark with `no-print`.

- [ ] **Step 6: Integrate Live Resume Showcase (`#resume`)**
  - Wrap master resume in `#resume-paper`.
  - Add persona switcher pills (`Fullstack`, `DevOps`, `Designer`, `Finance`, `Engineering`) and ATS toggle button in a `.no-print` control bar above `#resume-paper`.

- [ ] **Step 7: Add Download CTA Band (`#download`) & Editorial Footer**
  - Light gray banner (`#e0e2e6`) with direct download button for `/download/resume-template-starter.zip`.
  - White canvas 6-column link footer. Both marked with `no-print`.

- [ ] **Step 8: Run automated tests to verify complete DOM integration**

Run: `python -m pytest tests/test_career_hub.py -v`  
Expected: PASS (all required IDs, prompts, and invariants satisfied)

- [ ] **Step 9: Commit `index.html`**

```bash
git add index.html
git commit -m "feat(hub): integrate airtable editorial career hub, prompt library, and skills directory"
```

---

### Task 5: Starter Kit ZIP Packaging Script (`scripts/bundle_starter_kit.py`)

**Files:**
- Create: `scripts/bundle_starter_kit.py`

- [ ] **Step 1: Write packaging script**
  - Packages into `download/resume-template-starter.zip`:
    - `index.html` (standalone master resume template)
    - `style.css` (complete styles)
    - `config/profile.example.json` and all 4 persona JSONs
    - `jobs/prompts/*.txt` and `jobs/prompts/*.md`
    - `skills/` (24 agent skills)
    - `daily-job-search-workflow.md` and `daily-job-search-links.md`
    - `engine/` automation engine scripts and `run_engine.py`
    - `README.md` and `LICENSE.txt`
  - Validates that the resulting ZIP is non-empty and valid.

- [ ] **Step 2: Run packaging script and verify zip creation**

Run: `python scripts/bundle_starter_kit.py`  
Expected: Created `download/resume-template-starter.zip` (~100-300 KB)

- [ ] **Step 3: Add test in `tests/test_career_hub.py` checking ZIP bundle contents**

Run: `python -m pytest tests/test_career_hub.py -v`  
Expected: PASS

- [ ] **Step 4: Commit packaging script**

```bash
git add scripts/bundle_starter_kit.py tests/test_career_hub.py
git commit -m "feat(build): add starter kit bundling script"
```

---

### Task 6: Coolify Containerization (`Dockerfile`, `Caddyfile`, `docker-compose.yml`, `.dockerignore`)

**Files:**
- Create: `Caddyfile`
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `.dockerignore`

- [ ] **Step 1: Write `Caddyfile`**
  - Port `:80`
  - `encode gzip zstd`
  - `file_server`
  - `try_files {path} /index.html`
  - Security headers: `X-Content-Type-Options nosniff`, `X-Frame-Options SAMEORIGIN`, `Referrer-Policy strict-origin-when-cross-origin`
  - Cache control rules: HTML `no-cache`, static assets immutable 1y.

- [ ] **Step 2: Write `Dockerfile`**
  - Base: `caddy:2-alpine`
  - Copy public static files (`index.html`, `style.css`, `hub.js`, portraits, `download/`) into `/usr/share/caddy`
  - Copy `Caddyfile` to `/etc/caddy/Caddyfile`
  - Expose port 80

- [ ] **Step 3: Write `docker-compose.yml` & `.dockerignore`**
  - Service `career-hub` with healthcheck: `wget -q --spider http://localhost:80/ || exit 1`
  - `.dockerignore` excluding `.git`, `.venv`, `__pycache__`, local scratch scripts, and temporary PDF outputs.

- [ ] **Step 4: Commit Coolify configuration**

```bash
git add Caddyfile Dockerfile docker-compose.yml .dockerignore
git commit -m "feat(deploy): add alpine caddy container and coolify compose orchestration"
```

---

### Task 7: Full End-to-End Verification & Healthcheck

**Files:**
- Verify: all project files, DOM validation, container sanity.

- [ ] **Step 1: Run comprehensive test suite**

Run: `python -m pytest tests/test_career_hub.py -v`  
Expected: ALL PASS

- [ ] **Step 2: Run resume engine validation to guarantee ATS DOM compliance**

Run: `python jobs/engine.py validate-resume --file index.html`  
Expected: PASS with 0 DOM structural errors

- [ ] **Step 3: Verify git status is clean**

Run: `git status -s`  
Expected: Clean working tree

- [ ] **Step 4: Final commit & deployment tag**

```bash
git commit --allow-empty -m "chore(release): career hub ready for coolify deployment on career.masrisystems.com"
```
