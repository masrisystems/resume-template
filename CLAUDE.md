# CLAUDE.md - WebResume Guidelines

Authoritative guidelines, candidate invariants, automation engine commands, and formatting rules are defined in:
👉 [AGENTS.md](AGENTS.md)

## Common Commands
- Run pipeline: `python jobs/engine.py run --config jobs/configs/YYYY-MM-DD_[company_slug].json`
- Build canonical roles: `python jobs/engine.py build-roles`
- Render search links dashboard: `python jobs/engine.py build-links`
- Validate resume: `python jobs/engine.py validate-resume --file index.html`

## Claude Code Specifics
- Preserve `index.html` as the source of truth for the master resume.
- All candidate profile data and contractual invariants are loaded from `config/profile.json` (or fallback `config/profile.example.json`).
- Never use emojis in UI or PDFs. Use spaced compound terms (e.g. `REST APIs`, `Fullstack Entwickler`).
