import os
import zipfile
from pathlib import Path

def build_starter_kit():
    root_dir = Path(__file__).resolve().parent.parent
    output_dir = root_dir / "download"
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / "resume-template-starter.zip"

    # Specific files and directories to include
    include_files = [
        "index.html",
        "resume.html",
        "resume.js",
        "download.html",
        "style.css",
        "hub.js",
        "README.md",
        "LICENSE.txt",
        "AGENTS.md",
        "daily-job-search-workflow.md",
        "daily-job-search-links.md",
        "alex-morgan-profile.webp",
        "stefan-kramer-profile.webp",
        "run_engine.py",
    ]

    include_dirs = [
        "assets",
        "workflows",
        "config",
        "engine",
        "jobs/prompts",
        "jobs/roles",
        "skills",
    ]

    print(f"Bundling starter kit to: {zip_path}")
    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        # Add root files
        for rel_file in include_files:
            file_path = root_dir / rel_file
            if file_path.exists():
                z.write(file_path, arcname=f"resume-template/{rel_file}")
                count += 1

        # Add directory trees
        for rel_dir in include_dirs:
            dir_path = root_dir / rel_dir
            if dir_path.exists():
                for root, dirs, files in os.walk(dir_path):
                    # Filter out __pycache__ and hidden files
                    dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
                    for file in files:
                        if file.startswith(".") or file.endswith(".pyc"):
                            continue
                        # Never bundle private user profile
                        if rel_dir == "config" and file == "profile.json":
                            continue
                        full_path = Path(root) / file
                        arcname = f"resume-template/{full_path.relative_to(root_dir)}"
                        z.write(full_path, arcname=arcname)
                        count += 1

    size_kb = zip_path.stat().st_size / 1024
    print(f"[OK] Starter kit bundled successfully: {count} files, {size_kb:.1f} KB")
    return zip_path

if __name__ == "__main__":
    build_starter_kit()
