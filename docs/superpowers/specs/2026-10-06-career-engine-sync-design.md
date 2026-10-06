# Career Engine & WebResume Integration and Symmetrical Sync Design

- **Date**: 2026-10-06
- **Status**: Draft (Approved in Brainstorming)
- **Author**: Masri Systems & Antigravity
- **Target Repositories**:
  - Public Framework: `resume-template` (`https://github.com/masrisystems/resume-template` at `C:\Users\super\Projects\obsidian\resume-template`)
  - Private Portfolio & Pipeline: `WebResume` (`https://github.com/masrisystems/resume` at `C:\Users\super\Projects\obsidian\masrisystems-app\content\private\Career\WebResume`)

---

## 1. Context and Problem Statement

`resume-template` was originally cloned from `WebResume` to create an open-source, ATS-optimized web resume template and Career Engine product.
Over time, `resume-template` evolved significantly:
- Refactored `engine/` into a modular Python package (`cli.py`, `config.py`, `cover_letter.py`, `pdf.py`, `resume.py`, `search_links.py`).
- Added a full test suite (`tests/`).
- Created a rich Career Hub landing page (`index.html`) with Airtable-inspired design tokens, prompt library, and workflow simulation deck.
- Decoupled `resume.html` and `resume.js` powered by a single source of truth (`config/profile.json`).

Meanwhile, active job hunting continued in `WebResume`:
- 19+ new company application packages were created (`jobs/configs/2026-09-25_*.json` through `jobs/configs/2026-10-06_*.json`), with corresponding cover letters and resumes.
- `index.html` remains Mohamad Masri's live resume published on `https://masrisystems.com` via GitHub Actions to Uberspace.
- `WebResume` is still running the legacy 34KB monolithic `jobs/engine.py` and standalone legacy helper scripts.

Currently, any improvement to prompts, canonical roles, search links, or engine capabilities made in either repository must be manually copy-pasted, leading to drift and risks of regressions or accidental PII leaks.

---

## 2. Goals & Invariants

### 2.1 Goals
1. **Symmetrical Framework Synchronization**: Seamlessly sync framework code, AI prompts, canonical role archetypes, and testing suites between `resume-template` and `WebResume`.
2. **Zero-Access PII and Private Data Isolation**: Guarantee that personal data (Mohamad Masri's real address, phone, salary invariants, company application JSONs, company-specific cover letters and resumes) NEVER leaks into the public `resume-template` repository.
3. **Zero Disruption to Active Pipeline**: Ensure all 19+ active job applications in `WebResume` continue working without modification.
4. **Dual Tooling**: Provide both an engine CLI subcommand (`python jobs/engine.py sync`) and an interactive PowerShell script (`sync-career-engine.ps1`).
5. **Bidirectional Intelligence**: Support preview (`status` / `--dry-run`), directional sync (`push` / `pull`), and automated timestamp/hash-based sync (`auto`).

### 2.2 Strict Invariants
- **No PII Export**: `config/profile.json` in `WebResume` contains real personal data and must NEVER be synced to `resume-template`. `resume-template` must retain sanitized example personas (`Alex Morgan`, `Stefan Kramer`, etc.).
- **Private Jobs Isolation**: `jobs/configs/*`, `jobs/cover_letters/*`, `jobs/resumes/*`, `jobs/job_descriptions/*`, and `jobs/job_matches.md` are local to `WebResume` and blocked from syncing to `resume-template`.
- **Root Web Page Independence**: `index.html` in `WebResume` is the live resume (`masrisystems.com`), while `index.html` in `resume-template` is the Career Hub product landing page (`career.masrisystems.com`). They remain decoupled.
- **Git & Deployment Isolation**: `.git/`, `.github/workflows/`, and container deployment configs (`Caddyfile`, `Dockerfile`, `docker-compose.yml`) remain repository-specific.

---

## 3. Architecture & Sync Boundaries

### 3.1 Whitelist Manifest (Synchronized Paths)
The sync system manages the following whitelisted relative paths:

```json
{
  "sync_manifest": [
    "engine/",
    "jobs/engine.py",
    "jobs/prompts/",
    "jobs/roles/",
    "tests/",
    "workflows/",
    "daily-job-search-workflow.md",
    "scripts/"
  ]
}
```

### 3.2 Blacklist (Never Synced)
The following paths are strictly blocked from being pushed to `resume-template`:
- `config/profile.json` (Real PII)
- `jobs/configs/**` (Active company application configs)
- `jobs/cover_letters/**` (Company-specific cover letters)
- `jobs/resumes/**` (Company-specific tailored resumes)
- `jobs/job_descriptions/**` (Scraped company postings)
- `jobs/job_matches.md` (Personal CRM)
- `masrisystems-mohamad-masri-*` (Personal portraits)
- `index.html` (Live resume vs Career Hub)
- `Caddyfile`, `Dockerfile`, `docker-compose.yml`
- `.git/**`, `.github/**`, `.gemini/**`, `.vscode/**`

---

## 4. Component Design

### 4.1 Modular Python Engine Module: `engine/sync.py`
A new module added to the `engine` package implementing the core sync logic:

```python
class CareerEngineSync:
    def __init__(self, source_root: Path, target_root: Path): ...
    def scan(self) -> List[FileStatus]: ...
    def status(self) -> None: ...
    def push(self, dry_run: bool = False) -> SyncResult: ...
    def pull(self, dry_run: bool = False) -> SyncResult: ...
    def auto(self, dry_run: bool = False) -> SyncResult: ...
```

#### Status Enum:
- `IDENTICAL`: SHA-256 matches. No action needed.
- `LOCAL_NEWER`: Local file has newer mtime and content differs.
- `TARGET_NEWER`: Target file has newer mtime and content differs.
- `NEW_LOCAL`: File exists locally in manifest, missing in target.
- `NEW_TARGET`: File exists in target manifest, missing locally.
- `BLOCKED`: File matches blacklist (e.g., attempt to sync PII to template).

### 4.2 CLI Integration: `engine/cli.py`
Add `sync` subcommand to the argparse tree:
```text
python jobs/engine.py sync [status|push|pull|auto] [--target <path>] [--dry-run]
```

Defaults:
- In `resume-template`: default target is `C:\Users\super\Projects\obsidian\masrisystems-app\content\private\Career\WebResume`.
- In `WebResume`: default target is `C:\Users\super\Projects\obsidian\resume-template`.

### 4.3 Interactive PowerShell Script: `sync-career-engine.ps1`
Mirrors `C:\Users\super\.agents\sync.ps1`:
- `.\sync-career-engine.ps1` without flags runs `-Preview` (safe dry run).
- `.\sync-career-engine.ps1 -Apply` applies changes.
- Parameters:
  - `-Direction <Auto|Push|Pull>` (Default: `Auto`)
  - `-Target <path>` (Optional override)
  - `-Force` (Bypass confirmation prompt)

---

## 5. WebResume Baseline Migration Plan

To align `WebResume` with the new framework:
1. Copy `engine/` package from `resume-template` into `WebResume/engine/`.
2. Add `engine/sync.py` and register the `sync` subcommand.
3. Replace monolithic `WebResume/jobs/engine.py` with the delegating 15-line entry point.
4. Clean up / deprecate redundant standalone scripts in `WebResume/jobs/` while ensuring backward compatibility.
5. Copy `sync-career-engine.ps1` to `WebResume/`.
6. Run `python jobs/engine.py validate-resume --file index.html` in `WebResume` to verify DOM and invariants.
7. Run `python jobs/engine.py sync status` in both repos to confirm clean baseline.

---

## 6. Testing & Verification

1. **Unit Tests**: Add `tests/test_sync.py` verifying:
   - Manifest scanning and SHA-256 hashing.
   - Strict blocking of blacklisted paths (PII, job configs).
   - Push, pull, and auto behaviors with temporary directories.
2. **End-to-End Simulation**:
   - Create a test file in `jobs/prompts/test_prompt.md` in `resume-template`.
   - Run `python jobs/engine.py sync status` $\to$ verify `[PUSH]` is detected.
   - Run `python jobs/engine.py sync push` $\to$ verify file is created in `WebResume`.
   - Clean up test file and sync deletion.
3. **Validation of Existing WebResume Workflows**:
   - Run `python jobs/engine.py run --config jobs/configs/2026-10-06_ecommerce_one.json --dry-run` in `WebResume` to verify active application generation works seamlessly.
