import json
import urllib.parse
from pathlib import Path
from .config import BASE_DIR, CONFIGS_DIR, load_profile


def init_config(slug: str, date_str: str, role_id: str = "fullstack_laravel") -> Path:
    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = CONFIGS_DIR / f"{date_str}_{slug}.json"
    if out_file.exists():
        print(f"[WARN] Config already exists: {out_file}")
        return out_file

    profile = load_profile()
    cand = profile.get("candidate", {})
    inv = profile.get("invariants", {})
    sal_phrase = inv.get("target_salary_phrase_de", "65.000 Euro brutto im Jahr")
    notice_phrase = inv.get(
        "notice_period_de",
        "dreimonatigen Kündigungsfrist zum Monatsende, im Einvernehmen gern auch kurzfristiger",
    )
    sender_title = cand.get("title_de", "Senior Fullstack Entwickler · PHP, Laravel & Vue.js")
    city = inv.get("default_location_city", "Berlin")

    skeleton = {
        "slug": slug,
        "date": date_str,
        "role_profile": role_id,
        "cover_letter": {
            "company_clean": f"{slug.capitalize()} GmbH",
            "sender_title": sender_title,
            "recipient_company": f"{slug.capitalize()} GmbH",
            "recipient_person": "Recruiting Team",
            "recipient_address": f"Musterstraße 1 · {city}",
            "subject_line": "Bewerbung als Senior Fullstack Engineer (m/w/d)",
            "salutation": "Sehr geehrte Damen und Herren,",
            "paragraphs": [
                f"Technologische Exzellenz und moderne Architekturen bilden das Fundament robuster Softwarelösungen. Die Ausrichtung von {slug.capitalize()} GmbH passt ideal zu meinem Profil.",
                "Seit über fünf Jahren entwickle und skaliere ich moderne Webanwendungen auf Basis von PHP, Laravel, TypeScript und Vue.js. Ein starker Fokus liegt dabei auf sauberen Schnittstellen, automatisierten Tests und CI/CD-Pipelines.",
                f"Meinen Gehaltsrahmen beziffere ich mit {sal_phrase}. Meine Verfügbarkeit richtet sich nach einer {notice_phrase}. Detaillierte Arbeitsproben finden Sie unter {cand.get('links_url', 'https://links.example.com')}. Ich freue mich auf den fachlichen Austausch.",
            ],
        },
    }

    out_file.write_text(json.dumps(skeleton, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Initialized skeleton config with role '{role_id}': {out_file}")
    return out_file


def build_daily_search_links(output_file: str = None) -> Path:
    profile = load_profile()
    cand = profile.get("candidate", {})
    inv = profile.get("invariants", {})
    sp = profile.get("search_preferences", {})
    platforms = profile.get("search_platforms", [])
    best_practices = profile.get("best_practices", [])

    target_stack = ", ".join(sp.get("target_stack", []))
    exp_level = sp.get("experience_level", "Senior Level (5+ Jahre Erfahrung)")
    location = sp.get("location", "Berlin")
    postal_code = sp.get("postal_code", "10115")
    radius_km = sp.get("radius_km", 25)
    remote_focus = sp.get("remote_focus", "100% Remote (Deutschland/Europa) oder Hybrid Berlin")
    sal_band = sp.get("salary_band", {})
    min_eur = sal_band.get("min_eur", 60000)
    max_eur = sal_band.get("max_eur", 75000)
    target_phrase = inv.get("target_salary_phrase_de", "65.000 Euro brutto im Jahr")
    role_keyword = sp.get("role_keyword") or (cand.get("title_en", "Developer").split()[0])

    role_quoted = urllib.parse.quote_plus(role_keyword)
    loc_quoted = urllib.parse.quote_plus(location)

    table_rows = []
    for idx, p in enumerate(platforms, 1):
        name = p.get("name", "Platform")
        cat = p.get("category", "")
        tmpl = p.get("url_template", "")
        rendered_url = (
            tmpl.replace("{role}", role_quoted)
            .replace("{location}", loc_quoted)
            .replace("{postal_code}", postal_code)
            .replace("{radius_km}", str(radius_km))
        )
        table_rows.append(
            f"| **{idx}** | **{name}** | {cat} · {location} (+{radius_km} km) | [Direktlink]({rendered_url}) |"
        )

    bp_items = "\n".join(f"- {bp}" for bp in best_practices)

    content = f"""---
tags: [career, job-search, daily-routine, links, queries, web-resume]
title: Daily Job Discovery Quick-Links & Saved Search Queries
created: 2026-10-01
---

# 🔎 Daily Job Discovery Quick-Links & Direct Search Queries

Dieses Dokument dient als tägliches Schnellstart-Dashboard für die manuelle und automatisierte Jobrecherche. Alle Links und Parameter werden zentral aus der Profilkonfiguration gesteuert:

- **Kandidat:** {cand.get('name', 'Alex Morgan')} ({cand.get('title_de', cand.get('title_en', 'Software Engineer'))})
- **Zielstack:** {target_stack}
- **Erfahrungslevel:** {exp_level}
- **Region:** {location} ({postal_code}, Umkreis {radius_km} km) sowie {remote_focus}
- **Gehaltsband-Fokus:** {min_eur:,} € – {max_eur:,} € (Ziel: {target_phrase})

---

## ⚡ Schnellstart: Das 10-Minuten-Morgen-Set

| # | Plattform | Kategorie & Parameter | Direktlink |
| :-: | :--- | :--- | :--- |
""" + "\n".join(table_rows) + f"""

---

## 💡 Best Practices für die tägliche Bewerbungsroutine

{bp_items}
"""

    out_path = Path(output_file) if output_file else (BASE_DIR / "daily-job-search-links.md")
    out_path.write_text(content, encoding="utf-8")
    print(f"[OK] Rendered SSOT Daily Search Links: {out_path.name}")
    return out_path
