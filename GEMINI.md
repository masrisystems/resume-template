# Gemini & Antigravity Guidelines - WebResume

Authoritative guidelines, candidate invariants, automation engine commands, and formatting rules are defined in:
👉 [AGENTS.md](AGENTS.md)

## Gemini / Antigravity Execution Notes

- **Single Source of Truth**: All candidate profile parameters and invariants are loaded dynamically from `config/profile.json` (or `config/profile.example.json`).
- **Automation Engine**: Always execute application generation via `python jobs/engine.py run --config ...`.
- **Zero Scratch Scripts**: Never create temporary scratch scripts (`test_*.py`, `inspect_*.py`).
- **Programmatic Validation**: Do not capture visual screenshots or render PNGs. Verify output via DOM inspection and PDF text validation.
- **Contractual Invariants**: Enforce notice period and salary target from `config/profile.json` across all cover letters and portal profiles.
