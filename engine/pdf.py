import os
import shutil
import subprocess
from pathlib import Path
from .config import RESUMES_DIR, COVER_LETTERS_DIR, sync_stylesheets


def find_browser() -> str:
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


def html_to_pdf(browser_exe: str, input_html: Path, output_pdf: Path) -> Path:
    input_html = Path(input_html).resolve()
    output_pdf = Path(output_pdf).resolve()

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    file_url = input_html.as_uri()

    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={str(output_pdf)}",
        file_url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if not output_pdf.exists() or output_pdf.stat().st_size == 0:
        raise RuntimeError(f"Failed to generate PDF for {input_html}.\nOutput: {result.stdout}\nError: {result.stderr}")

    print(f"[OK] Generated PDF: {output_pdf.name} ({output_pdf.stat().st_size} bytes)")
    return output_pdf


def export_pdfs(company_slug: str = None, date_str: str = None, all_files: bool = False):
    sync_stylesheets()
    browser_exe = find_browser()

    if company_slug and date_str:
        res_html = RESUMES_DIR / f"{company_slug}.html"
        if res_html.exists():
            res_pdf_slug = RESUMES_DIR / f"{company_slug}.pdf"
            html_to_pdf(browser_exe, res_html, res_pdf_slug)
            res_pdf_dated = RESUMES_DIR / f"{date_str}_{company_slug}.pdf"
            shutil.copy2(res_pdf_slug, res_pdf_dated)
            print(f"[OK] Copied dated Resume PDF: {res_pdf_dated.name}")

        cl_html = COVER_LETTERS_DIR / f"{date_str}_{company_slug}.html"
        if cl_html.exists():
            cl_pdf = COVER_LETTERS_DIR / f"{date_str}_{company_slug}.pdf"
            html_to_pdf(browser_exe, cl_html, cl_pdf)

    elif date_str:
        for cl in sorted(COVER_LETTERS_DIR.glob(f"{date_str}_*.html")):
            slug = cl.stem[len(date_str) + 1 :]
            export_pdfs(company_slug=slug, date_str=date_str)

    elif all_files:
        for cl in sorted(COVER_LETTERS_DIR.glob("*.html")):
            html_to_pdf(browser_exe, cl, cl.with_suffix(".pdf"))
        for res in sorted(RESUMES_DIR.glob("*.html")):
            html_to_pdf(browser_exe, res, res.with_suffix(".pdf"))
