import argparse
import json
from pathlib import Path

from .config import COVER_LETTERS_DIR, RESUMES_DIR, set_active_profile
from .cover_letter import build_cover_letter_from_config, validate_cover_letter_file
from .pdf import export_pdfs
from .resume import build_all_roles, build_resume_from_config, validate_resume_file
from .search_links import build_daily_search_links, init_config


def run_end_to_end(config_path: str):
    print(f"\n=== Executing End-to-End Application Package from {config_path} ===")
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    build_resume_from_config(config_path)
    build_cover_letter_from_config(config_path)
    export_pdfs(company_slug=cfg["slug"], date_str=cfg["date"])
    print(f"\n[SUCCESS] All application assets generated, validated, and exported for {cfg['slug']}!\n")


def main():
    parser = argparse.ArgumentParser(description="Unified Daily Job Application Engine")
    parser.add_argument("--profile", help="Path to profile JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_init = subparsers.add_parser("init-config", help="Initialize skeleton config")
    p_init.add_argument("--slug", required=True)
    p_init.add_argument("--date", required=True)
    p_init.add_argument("--role", default="fullstack_laravel")

    p_roles = subparsers.add_parser("build-roles", help="Build canonical role resumes")
    p_roles.add_argument("--role")

    p_links = subparsers.add_parser("build-links", help="Render daily search links")
    p_links.add_argument("--output")

    p_res = subparsers.add_parser("build-resume", help="Generate HTML resume")
    p_res.add_argument("--config", required=True)

    p_vres = subparsers.add_parser("validate-resume", help="Validate resume HTML")
    p_vres.add_argument("--file")
    p_vres.add_argument("--slug")

    p_cl = subparsers.add_parser("build-cover-letter", help="Generate cover letter")
    p_cl.add_argument("--config", required=True)

    p_vcl = subparsers.add_parser("validate-cover-letter", help="Validate cover letter")
    p_vcl.add_argument("--file")
    p_vcl.add_argument("--date")
    p_vcl.add_argument("--all", action="store_true")

    p_pdf = subparsers.add_parser("export-pdfs", help="Generate PDFs")
    p_pdf.add_argument("--config")
    p_pdf.add_argument("--slug")
    p_pdf.add_argument("--date")
    p_pdf.add_argument("--all", action="store_true")

    p_run = subparsers.add_parser("run", help="Run full pipeline")
    p_run.add_argument("--config", required=True)

    args = parser.parse_args()
    if args.profile:
        set_active_profile(args.profile)

    if args.command == "init-config":
        init_config(args.slug, args.date, role_id=args.role)
    elif args.command == "build-roles":
        build_all_roles(specific_role=args.role)
    elif args.command == "build-links":
        build_daily_search_links(output_file=getattr(args, "output", None))
    elif args.command == "build-resume":
        build_resume_from_config(args.config)
    elif args.command == "validate-resume":
        target = args.file if args.file else (RESUMES_DIR / f"{args.slug}.html")
        validate_resume_file(target)
    elif args.command == "build-cover-letter":
        build_cover_letter_from_config(args.config)
    elif args.command == "validate-cover-letter":
        if args.file:
            validate_cover_letter_file(args.file)
        elif args.date:
            for f in sorted(COVER_LETTERS_DIR.glob(f"{args.date}_*.html")):
                validate_cover_letter_file(f)
        elif args.all:
            for f in sorted(COVER_LETTERS_DIR.glob("*.html")):
                validate_cover_letter_file(f)
    elif args.command == "export-pdfs":
        slug, date_str = args.slug, args.date
        if args.config:
            cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
            slug, date_str = cfg["slug"], cfg["date"]
        export_pdfs(company_slug=slug, date_str=date_str, all_files=args.all)
    elif args.command == "run":
        run_end_to_end(args.config)


if __name__ == "__main__":
    main()
