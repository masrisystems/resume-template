import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JOBS_DIR = BASE_DIR / "jobs"
RESUMES_DIR = JOBS_DIR / "resumes"
COVER_LETTERS_DIR = JOBS_DIR / "cover_letters"

def find_browser():
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("chrome"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        shutil.which("msedge"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    raise RuntimeError("No headless Chrome or Edge browser executable found on this system.")

def html_to_pdf(browser_exe, input_html, output_pdf):
    input_html = Path(input_html).resolve()
    output_pdf = Path(output_pdf).resolve()

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    file_url = input_html.as_uri()

    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={str(output_pdf)}",
        file_url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if not output_pdf.exists() or output_pdf.stat().st_size == 0:
        raise RuntimeError(f"Failed to generate PDF for {input_html}.\nOutput: {result.stdout}\nError: {result.stderr}")

    print(f"Generated PDF: {output_pdf} ({output_pdf.stat().st_size} bytes)")
    return output_pdf

def generate_for_target(browser_exe, company_slug, date_str=None):
    # 1. Resume
    resume_html = RESUMES_DIR / f"{company_slug}.html"
    if resume_html.exists():
        # Standard slug-based PDF
        resume_pdf_slug = RESUMES_DIR / f"{company_slug}.pdf"
        html_to_pdf(browser_exe, resume_html, resume_pdf_slug)

        # Date-prefixed PDF if date given
        if date_str:
            resume_pdf_dated = RESUMES_DIR / f"{date_str}_{company_slug}.pdf"
            shutil.copy2(resume_pdf_slug, resume_pdf_dated)
            print(f"Copied dated Resume PDF: {resume_pdf_dated}")

    # 2. Cover Letter
    if date_str:
        cl_html = COVER_LETTERS_DIR / f"{date_str}_{company_slug}.html"
        if cl_html.exists():
            cl_pdf = COVER_LETTERS_DIR / f"{date_str}_{company_slug}.pdf"
            html_to_pdf(browser_exe, cl_html, cl_pdf)
    else:
        # Search for any matching cover letter
        for cl_file in COVER_LETTERS_DIR.glob(f"*_{company_slug}.html"):
            cl_pdf = cl_file.with_suffix(".pdf")
            html_to_pdf(browser_exe, cl_file, cl_pdf)

def main():
    parser = argparse.ArgumentParser(description="Convert Tailored Resumes and Cover Letters to PDF")
    parser.add_argument("--company", type=str, help="Company slug (e.g. mobiko)")
    parser.add_argument("--date", type=str, help="Application date (YYYY-MM-DD)")
    parser.add_argument("--all", action="store_true", help="Generate PDFs for all cover letters and resumes")
    args = parser.parse_args()

    browser_exe = find_browser()
    print(f"Using browser for PDF export: {browser_exe}")

    if args.company:
        generate_for_target(browser_exe, args.company, args.date)
    elif args.all:
        # Convert all cover letters
        for cl in sorted(COVER_LETTERS_DIR.glob("*.html")):
            cl_pdf = cl.with_suffix(".pdf")
            html_to_pdf(browser_exe, cl, cl_pdf)

        # Convert all tailored resumes
        for res in sorted(RESUMES_DIR.glob("*.html")):
            res_pdf = res.with_suffix(".pdf")
            html_to_pdf(browser_exe, res, res_pdf)
    elif args.date:
        for cl in sorted(COVER_LETTERS_DIR.glob(f"{args.date}_*.html")):
            company_slug = cl.stem[len(args.date) + 1:]
            generate_for_target(browser_exe, company_slug, args.date)
    else:
        # Default: check today's date or convert recent 2026-09-23
        default_date = "2026-09-23"
        print(f"No options specified, generating for date: {default_date}")
        for cl in sorted(COVER_LETTERS_DIR.glob(f"{default_date}_*.html")):
            company_slug = cl.stem[len(default_date) + 1:]
            generate_for_target(browser_exe, company_slug, default_date)

if __name__ == "__main__":
    main()
