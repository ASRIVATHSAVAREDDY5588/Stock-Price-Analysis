"""Build clean standalone distribution deliverable zip."""

import os
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
DIST_DIR.mkdir(parents=True, exist_ok=True)
ZIP_PATH = DIST_DIR / "Stock_Return_AI_Lab.zip"

EXCLUDE_DIRS = {".git", ".pytest_cache", "__pycache__", ".venv", ".cache", "dist", "Stock_Return_AI_Lab", "presentation_extraction"}
EXCLUDE_EXTS = {".pyc", ".pyo"}


def create_zip():
    print(f"Building clean deliverable zip: {ZIP_PATH}...")
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.endswith(".egg-info")]
            for file in files:
                if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue
                file_path = Path(root) / file
                if file_path == ZIP_PATH:
                    continue
                arcname = file_path.relative_to(PROJECT_ROOT)
                zf.write(file_path, arcname)

    # Also copy to parent dist if needed
    parent_dist = PROJECT_ROOT.parent / "dist"
    if parent_dist.exists():
        import shutil
        shutil.copy2(ZIP_PATH, parent_dist / "Stock_Return_AI_Lab.zip")

    size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    print(f"Deliverable package created: {ZIP_PATH} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    create_zip()
