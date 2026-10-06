# Career Engine & WebResume Symmetrical Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a manifest-driven, bidirectional synchronization engine and PowerShell wrapper to safely sync framework code, modular engine tools, canonical roles, and AI prompts between public `resume-template` and private `WebResume` while strictly isolating candidate PII and private job applications.

**Architecture:** A standalone Python module `engine/sync.py` manages a declarative manifest of whitelisted framework files and a strict blacklist of private directories. A CLI subcommand `python jobs/engine.py sync` and an interactive PowerShell script `sync-career-engine.ps1` expose status preview, push, pull, and auto-sync modes symmetrically in both repositories.

**Tech Stack:** Python 3.10+ (`pathlib`, `hashlib`, `shutil`, `argparse`), PowerShell 7+ (`pwsh`), pytest.

---

### Task 1: Core Sync Engine Module & Safety Boundary

**Files:**
- Create: `engine/sync.py`
- Create: `tests/test_sync.py`

- [ ] **Step 1: Write failing unit tests for `engine/sync.py`**

Create `tests/test_sync.py`:
```python
from pathlib import Path
import pytest
from engine.sync import CareerEngineSync, SyncStatus, FileSyncItem

@pytest.fixture
def sync_env(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    # Framework dirs
    (source / "engine").mkdir()
    (target / "engine").mkdir()
    (source / "jobs" / "prompts").mkdir(parents=True)
    (target / "jobs" / "prompts").mkdir(parents=True)

    # Identical file
    (source / "engine" / "cli.py").write_text("print('hello')", encoding="utf-8")
    (target / "engine" / "cli.py").write_text("print('hello')", encoding="utf-8")

    # Local newer file
    (source / "engine" / "pdf.py").write_text("print('v2')", encoding="utf-8")
    (target / "engine" / "pdf.py").write_text("print('v1')", encoding="utf-8")

    # Private file that MUST be blocked
    (source / "jobs" / "configs").mkdir(parents=True)
    (source / "jobs" / "configs" / "2026-10-06_test.json").write_text('{"company":"secret"}', encoding="utf-8")

    return source, target

def test_scan_detects_identical_and_modified(sync_env):
    source, target = sync_env
    syncer = CareerEngineSync(source_root=source, target_root=target)
    items = syncer.scan()

    cli_item = next(i for i in items if i.rel_path == "engine/cli.py")
    assert cli_item.status == SyncStatus.IDENTICAL

    pdf_item = next(i for i in items if i.rel_path == "engine/pdf.py")
    assert pdf_item.status in (SyncStatus.PUSH_NEEDED, SyncStatus.LOCAL_NEWER)

def test_blocked_paths_are_strictly_isolated(sync_env):
    source, target = sync_env
    syncer = CareerEngineSync(source_root=source, target_root=target)
    items = syncer.scan()

    # Ensure private job configs are not in sync list or flagged as BLOCKED
    config_items = [i for i in items if "jobs/configs" in i.rel_path]
    for item in config_items:
        assert item.status == SyncStatus.BLOCKED

def test_push_and_pull_sync(sync_env):
    source, target = sync_env
    syncer = CareerEngineSync(source_root=source, target_root=target)
    
    # Push from source to target
    res = syncer.push()
    assert (target / "engine" / "pdf.py").read_text(encoding="utf-8") == "print('v2')"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_sync.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.sync'`

- [ ] **Step 3: Implement `engine/sync.py`**

Create `engine/sync.py`:
```python
from __future__ import annotations
import hashlib
import os
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

DEFAULT_WEBRESUME_PATH = Path(r"C:\Users\super\Projects\obsidian\masrisystems-app\content\private\Career\WebResume")
DEFAULT_TEMPLATE_PATH = Path(r"C:\Users\super\Projects\obsidian\resume-template")

WHITELIST_MANIFEST = [
    "engine",
    "jobs/engine.py",
    "jobs/prompts",
    "jobs/roles",
    "tests",
    "workflows",
    "daily-job-search-workflow.md",
    "scripts",
]

BLACKLIST_PATTERNS = [
    "config/profile.json",
    "jobs/configs",
    "jobs/cover_letters",
    "jobs/resumes",
    "jobs/job_descriptions",
    "jobs/job_matches.md",
    "index.html",
    "Caddyfile",
    "Dockerfile",
    "docker-compose.yml",
    ".git",
    ".github",
    ".gemini",
    ".vscode",
]

class SyncStatus(str, Enum):
    IDENTICAL = "IDENTICAL"
    LOCAL_NEWER = "LOCAL_NEWER"
    TARGET_NEWER = "TARGET_NEWER"
    NEW_LOCAL = "NEW_LOCAL"
    NEW_TARGET = "NEW_TARGET"
    BLOCKED = "BLOCKED"
    PUSH_NEEDED = "PUSH_NEEDED"
    PULL_NEEDED = "PULL_NEEDED"

@dataclass
class FileSyncItem:
    rel_path: str
    status: SyncStatus
    local_path: Optional[Path] = None
    target_path: Optional[Path] = None
    detail: str = ""

def compute_sha256(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def is_blacklisted(rel_str: str) -> bool:
    norm = rel_str.replace("\\", "/").strip("/")
    for b in BLACKLIST_PATTERNS:
        b_norm = b.replace("\\", "/").strip("/")
        if norm == b_norm or norm.startswith(b_norm + "/"):
            return True
    return False

class CareerEngineSync:
    def __init__(self, source_root: Path, target_root: Optional[Path] = None):
        self.source_root = Path(source_root).resolve()
        if target_root:
            self.target_root = Path(target_root).resolve()
        else:
            # Symmetrical default resolution
            if "resume-template" in str(self.source_root):
                self.target_root = DEFAULT_WEBRESUME_PATH.resolve()
            else:
                self.target_root = DEFAULT_TEMPLATE_PATH.resolve()

    def scan(self) -> List[FileSyncItem]:
        results: List[FileSyncItem] = []
        visited = set()

        for entry in WHITELIST_MANIFEST:
            src_entry = self.source_root / entry
            tgt_entry = self.target_root / entry

            all_subpaths = set()
            if src_entry.exists():
                if src_entry.is_file():
                    all_subpaths.add(Path(entry))
                else:
                    for p in src_entry.rglob("*"):
                        if p.is_file():
                            all_subpaths.add(p.relative_to(self.source_root))
            if tgt_entry.exists():
                if tgt_entry.is_file():
                    all_subpaths.add(Path(entry))
                else:
                    for p in tgt_entry.rglob("*"):
                        if p.is_file():
                            all_subpaths.add(p.relative_to(self.target_root))

            for rel in sorted(all_subpaths):
                rel_str = str(rel).replace("\\", "/")
                if rel_str in visited:
                    continue
                visited.add(rel_str)

                if is_blacklisted(rel_str):
                    results.append(FileSyncItem(rel_path=rel_str, status=SyncStatus.BLOCKED, detail="Blocked by privacy policy"))
                    continue

                local_f = self.source_root / rel
                target_f = self.target_root / rel

                if local_f.exists() and not target_f.exists():
                    results.append(FileSyncItem(rel_path=rel_str, status=SyncStatus.NEW_LOCAL, local_path=local_f, detail="Only in local"))
                elif target_f.exists() and not local_f.exists():
                    results.append(FileSyncItem(rel_path=rel_str, status=SyncStatus.NEW_TARGET, target_path=target_f, detail="Only in target"))
                else:
                    local_hash = compute_sha256(local_f)
                    target_hash = compute_sha256(target_f)
                    if local_hash == target_hash:
                        results.append(FileSyncItem(rel_path=rel_str, status=SyncStatus.IDENTICAL, local_path=local_f, target_path=target_f, detail="Identical"))
                    else:
                        local_mtime = local_f.stat().st_mtime
                        target_mtime = target_f.stat().st_mtime
                        if local_mtime > target_mtime:
                            results.append(FileSyncItem(rel_path=rel_str, status=SyncStatus.LOCAL_NEWER, local_path=local_f, target_path=target_f, detail="Local newer"))
                        else:
                            results.append(FileSyncItem(rel_path=rel_str, status=SyncStatus.TARGET_NEWER, local_path=local_f, target_path=target_f, detail="Target newer"))

        return results

    def push(self, dry_run: bool = False) -> List[str]:
        items = self.scan()
        copied = []
        for item in items:
            if item.status in (SyncStatus.LOCAL_NEWER, SyncStatus.NEW_LOCAL, SyncStatus.PUSH_NEEDED):
                if is_blacklisted(item.rel_path):
                    continue
                dst = self.target_root / item.rel_path
                src = self.source_root / item.rel_path
                if not dry_run:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                copied.append(item.rel_path)
        return copied

    def pull(self, dry_run: bool = False) -> List[str]:
        items = self.scan()
        copied = []
        for item in items:
            if item.status in (SyncStatus.TARGET_NEWER, SyncStatus.NEW_TARGET, SyncStatus.PULL_NEEDED):
                if is_blacklisted(item.rel_path):
                    continue
                dst = self.source_root / item.rel_path
                src = self.target_root / item.rel_path
                if not dry_run:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                copied.append(item.rel_path)
        return copied

    def auto(self, dry_run: bool = False) -> List[str]:
        items = self.scan()
        synced = []
        for item in items:
            if is_blacklisted(item.rel_path) or item.status == SyncStatus.IDENTICAL:
                continue
            if item.status in (SyncStatus.LOCAL_NEWER, SyncStatus.NEW_LOCAL):
                dst = self.target_root / item.rel_path
                src = self.source_root / item.rel_path
                if not dry_run:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                synced.append(f"PUSH: {item.rel_path}")
            elif item.status in (SyncStatus.TARGET_NEWER, SyncStatus.NEW_TARGET):
                dst = self.source_root / item.rel_path
                src = self.target_root / item.rel_path
                if not dry_run:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                synced.append(f"PULL: {item.rel_path}")
        return synced
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_sync.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add engine/sync.py tests/test_sync.py
git commit -m "feat(sync): add CareerEngineSync module and unit test suite"
```

---

### Task 2: Register Sync Subcommand in Engine CLI

**Files:**
- Modify: `engine/cli.py`
- Modify: `tests/test_sync.py`

- [ ] **Step 1: Write CLI argument parsing test in `tests/test_sync.py`**

Add test to `tests/test_sync.py`:
```python
def test_sync_cli_status(monkeypatch, capsys, sync_env):
    source, target = sync_env
    from engine.cli import main
    monkeypatch.setattr("sys.argv", ["engine.py", "sync", "status", "--target", str(target)])
    monkeypatch.setattr("pathlib.Path.cwd", lambda: source)
    
    # Should exit cleanly or return 0
    main()
    captured = capsys.readouterr()
    assert "IDENTICAL" in captured.out or "engine/cli.py" in captured.out
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_sync.py::test_sync_cli_status -v`
Expected: FAIL with unrecognized arguments / command.

- [ ] **Step 3: Modify `engine/cli.py` to register `sync` parser**

Add `sync` subparser:
```python
from engine.sync import CareerEngineSync, SyncStatus

sync_parser = subparsers.add_parser("sync", help="Synchronize framework tooling between repos")
sync_sub = sync_parser.add_subparsers(dest="sync_command", default="status")

sync_status = sync_sub.add_parser("status", help="Preview sync status")
sync_status.add_argument("--target", help="Target repository directory path")

sync_push = sync_sub.add_parser("push", help="Push framework updates to target")
sync_push.add_argument("--target", help="Target repository directory path")
sync_push.add_argument("--dry-run", action="store_true", help="Preview without writing")

sync_pull = sync_sub.add_parser("pull", help="Pull framework updates from target")
sync_pull.add_argument("--target", help="Target repository directory path")
sync_pull.add_argument("--dry-run", action="store_true", help="Preview without writing")

sync_auto = sync_sub.add_parser("auto", help="Auto sync newer files bidirectionally")
sync_auto.add_argument("--target", help="Target repository directory path")
sync_auto.add_argument("--dry-run", action="store_true", help="Preview without writing")
```

Handler logic in `cli.py`:
```python
if args.command == "sync":
    syncer = CareerEngineSync(source_root=REPO_ROOT, target_root=Path(args.target) if getattr(args, "target", None) else None)
    cmd = getattr(args, "sync_command", "status") or "status"
    if cmd == "status":
        items = syncer.scan()
        print(f"\nComparing:\n  Source: {syncer.source_root}\n  Target: {syncer.target_root}\n")
        print(f"{'STATUS':<15} {'PATH':<45} DETAIL")
        print("-" * 75)
        for item in items:
            print(f"{item.status.value:<15} {item.rel_path:<45} {item.detail}")
    elif cmd == "push":
        res = syncer.push(dry_run=args.dry_run)
        print(f"Pushed {len(res)} files to {syncer.target_root}")
    elif cmd == "pull":
        res = syncer.pull(dry_run=args.dry_run)
        print(f"Pulled {len(res)} files from {syncer.target_root}")
    elif cmd == "auto":
        res = syncer.auto(dry_run=args.dry_run)
        print(f"Auto-synced {len(res)} changes.")
```

- [ ] **Step 4: Run test to verify PASS**

Run: `pytest tests/test_sync.py -v`
Expected: ALL PASS

- [ ] **Step 5: Verify via CLI live**

Run: `python jobs/engine.py sync status`
Expected: Output showing clean table of files.

- [ ] **Step 6: Commit**

```bash
git add engine/cli.py tests/test_sync.py
git commit -m "feat(cli): add sync command to jobs/engine.py"
```

---

### Task 3: Interactive PowerShell Sync Tooling

**Files:**
- Create: `sync-career-engine.ps1`

- [ ] **Step 1: Write `sync-career-engine.ps1`**

Create `sync-career-engine.ps1`:
```powershell
[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet("Auto", "Push", "Pull", "Status")]
    [string]$Direction = "Status",

    [Parameter()]
    [string]$Target,

    [Parameter()]
    [switch]$Apply,

    [Parameter()]
    [switch]$Preview
)

$ErrorActionPreference = "Stop"

# Auto-resolve target if not provided
$CurrentRepo = $PSScriptRoot
if (-not $Target) {
    if ($CurrentRepo -like "*resume-template*") {
        $Target = "C:\Users\super\Projects\obsidian\masrisystems-app\content\private\Career\WebResume"
    } else {
        $Target = "C:\Users\super\Projects\obsidian\resume-template"
    }
}

if (-not (Test-Path $Target)) {
    Write-Error "Target directory does not exist: $Target"
    exit 1
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Career Engine Symmetrical Sync Tool" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Source: $CurrentRepo" -ForegroundColor Gray
Write-Host "Target: $Target" -ForegroundColor Gray

# If neither -Apply nor direction specified other than status, run status
if (-not $Apply -or $Preview -or $Direction -eq "Status") {
    Write-Host "`nRunning read-only status preview..." -ForegroundColor Yellow
    python "$CurrentRepo\jobs\engine.py" sync status --target "$Target"
    Write-Host "`nTo apply changes, run with -Apply: .\sync-career-engine.ps1 -Apply -Direction <Auto|Push|Pull>`n" -ForegroundColor DarkGray
    exit 0
}

Write-Host "`nApplying synchronization (Direction: $Direction)..." -ForegroundColor Green
$cmdArgs = @("sync", $Direction.ToLower(), "--target", $Target)
python "$CurrentRepo\jobs\engine.py" @cmdArgs

Write-Host "`nSync complete!" -ForegroundColor Green
```

- [ ] **Step 2: Test script in PowerShell**

Run: `pwsh -Command ".\sync-career-engine.ps1"`
Expected: Displays table comparison in preview mode without modifying files.

- [ ] **Step 3: Commit**

```bash
git add sync-career-engine.ps1
git commit -m "feat(scripts): add sync-career-engine.ps1 PowerShell automation script"
```

---

### Task 4: WebResume Migration & Initial Framework Sync

**Files:**
- Target Repo: `C:\Users\super\Projects\obsidian\masrisystems-app\content\private\Career\WebResume`
  - Create: `WebResume/engine/` (synced from `resume-template/engine/`)
  - Replace: `WebResume/jobs/engine.py` (with clean delegator)
  - Create: `WebResume/sync-career-engine.ps1`
  - Create: `WebResume/tests/test_sync.py`
  - Sync: `WebResume/jobs/roles/`, `WebResume/jobs/prompts/`, `WebResume/workflows/`

- [ ] **Step 1: Execute `push` to upgrade WebResume**

Run: `python jobs/engine.py sync push`
Expected: Copies `engine/`, `sync-career-engine.ps1`, `tests/`, `workflows/`, and prompts into `WebResume`.

- [ ] **Step 2: Verify WebResume integrity with test suite and validator**

Run:
```bash
python -C "C:\Users\super\Projects\obsidian\masrisystems-app\content\private\Career\WebResume" jobs/engine.py validate-resume --file index.html
```
Expected: PASS (DOM structure valid, invariants satisfied).

- [ ] **Step 3: Verify existing active application configs run cleanly in WebResume**

Run:
```bash
pwsh -Command "python C:\Users\super\Projects\obsidian\masrisystems-app\content\private\Career\WebResume\jobs\engine.py run --config jobs/configs/2026-10-06_ecommerce_one.json --dry-run"
```
Expected: Application package builds cleanly without error.

- [ ] **Step 4: Commit baseline changes in WebResume repository**

Run:
```bash
git -C "C:\Users\super\Projects\obsidian\masrisystems-app\content\private\Career\WebResume" add engine/ jobs/engine.py sync-career-engine.ps1 tests/
git -C "C:\Users\super\Projects\obsidian\masrisystems-app\content\private\Career\WebResume" commit -m "feat(engine): upgrade to modular Career Engine architecture and symmetrical sync"
```

---

### Task 5: End-to-End Bidirectional Verification & Final Integration

**Files:**
- Test file: `jobs/prompts/test_sync_prompt.md`

- [ ] **Step 1: Test Push from `resume-template`**
Create a test file in `resume-template/jobs/prompts/test_sync_prompt.md`.
Run `python jobs/engine.py sync push`
Verify file exists in `WebResume/jobs/prompts/test_sync_prompt.md`.

- [ ] **Step 2: Test Pull from `WebResume`**
Modify `WebResume/jobs/prompts/test_sync_prompt.md`.
Run `python jobs/engine.py sync pull` in `resume-template`.
Verify updated content pulled into `resume-template`.

- [ ] **Step 3: Cleanup Test File**
Remove `test_sync_prompt.md` from both repositories.

- [ ] **Step 4: Verify Zero Leaks**
Run: `git status` in `resume-template` to verify no private files from `WebResume` (`jobs/configs/`, `config/profile.json` real data, etc.) appear in working directory or git tracking.

- [ ] **Step 5: Run full test suite across both repos**
Run: `pytest tests/` in `resume-template`.
Run: `pwsh -Command "pytest C:\Users\super\Projects\obsidian\masrisystems-app\content\private\Career\WebResume\tests"`
Expected: ALL PASS.
