import json
import re
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JOBS_DIR = BASE_DIR / "jobs"
RESUMES_DIR = JOBS_DIR / "resumes"
COVER_LETTERS_DIR = JOBS_DIR / "cover_letters"
JOB_DESCRIPTIONS_DIR = JOBS_DIR / "job_descriptions"
CONFIGS_DIR = JOBS_DIR / "configs"
ROLES_DIR = JOBS_DIR / "roles"
ROLES_HTML_DIR = ROLES_DIR / "html"
ROLES_PDF_DIR = ROLES_DIR / "pdf"
MASTER_INDEX = (BASE_DIR / "resume.html") if (BASE_DIR / "resume.html").exists() else (BASE_DIR / "index.html")
CONFIG_DIR = BASE_DIR / "config"

ACTIVE_PROFILE_PATH = None


def set_active_profile(profile_path: str):
    global ACTIVE_PROFILE_PATH
    ACTIVE_PROFILE_PATH = profile_path


def load_profile(profile_path: str = None) -> dict:
    path = profile_path or ACTIVE_PROFILE_PATH
    if path:
        cfg_file = Path(path)
        if cfg_file.exists():
            return json.loads(cfg_file.read_text(encoding="utf-8"))

    cfg_file = CONFIG_DIR / "profile.json"
    if not cfg_file.exists():
        cfg_file = CONFIG_DIR / "profile.example.json"
    if not cfg_file.exists():
        raise FileNotFoundError("Neither config/profile.json nor config/profile.example.json found.")
    return json.loads(cfg_file.read_text(encoding="utf-8"))


def sync_profile_to_resume():
    prof = load_profile()
    prof_copy = json.loads(json.dumps(prof))
    if "candidate" in prof_copy and "prohibited_domains" in prof_copy["candidate"]:
        del prof_copy["candidate"]["prohibited_domains"]

    res_p = BASE_DIR / "resume.html"
    if res_p.exists():
        content = res_p.read_text(encoding="utf-8")
        prof_json = json.dumps(prof_copy, indent=2, ensure_ascii=False)
        content = re.sub(
            r'<script id="profile-data" type="application/json">.*?</script>',
            f'<script id="profile-data" type="application/json">{prof_json}</script>',
            content,
            flags=re.DOTALL,
        )
        res_p.write_text(content, encoding="utf-8")


def sync_stylesheets():
    style_src = BASE_DIR / "style.css"
    js_src = BASE_DIR / "resume.js"
    ROLES_HTML_DIR.mkdir(parents=True, exist_ok=True)
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    if style_src.exists():
        shutil.copy2(style_src, ROLES_HTML_DIR / "style.css")
        shutil.copy2(style_src, RESUMES_DIR / "style.css")
    if js_src.exists():
        shutil.copy2(js_src, ROLES_HTML_DIR / "resume.js")
        shutil.copy2(js_src, RESUMES_DIR / "resume.js")
    for img in BASE_DIR.glob("*.webp"):
        shutil.copy2(img, ROLES_HTML_DIR / img.name)
        shutil.copy2(img, RESUMES_DIR / img.name)
    sync_profile_to_resume()


