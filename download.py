import os
import zipfile
from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).parent

EXCLUDE_DIRS = {
    "__pycache__", ".git", "env", "node_modules", ".idea", "venv", 
    "browser_sessions", "generated_videos", "temp_assets"
}
EXCLUDE_FILES = {
    "upload_history.json",
    "project_archive.zip"
}


def create_repo_zip() -> str:
    """Create a ZIP archive of the repository (excluding heavy/temporary files).
    Returns the absolute path to the created zip file.
    """
    zip_path = PROJECT_ROOT / "project_archive.zip"
    # Remove existing zip if present
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for folderpath, dirnames, filenames in os.walk(PROJECT_ROOT):
            # Convert to Path for easier checks
            folder = Path(folderpath)
            # Skip excluded dirs
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for filename in filenames:
                file_path = folder / filename
                # Skip excluded files by their name
                if file_path.name in EXCLUDE_FILES:
                    continue
                # Write file with relative path
                rel_path = file_path.relative_to(PROJECT_ROOT)
                zipf.write(file_path, rel_path)
    return str(zip_path)
