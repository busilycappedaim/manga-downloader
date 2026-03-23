from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
import re

def tocbz(output: Path, files: list[Path]) -> None:
    with ZipFile(output, "w", ZIP_DEFLATED) as zf:
        for f in files:
            p = Path(f)
            zf.write(p, arcname=p.name)

def make_cbz_path(title: str, chapter: str | None) -> Path:

    safe_title = re.sub(r'[<>:"/\\|?*]', '-', title)
    
    if chapter:
        safe_chapter = re.sub(r'[<>:"/\\|?*]', '-', chapter)
        return Path("downloads") / safe_title / f"{safe_chapter}.cbz"

    return Path("downloads") / f"{safe_title}.cbz"

def makeCBZ(cbz_path: Path, files: list[Path]) -> None:

    cbz_path.parent.mkdir(parents=True, exist_ok=True)

    tocbz(cbz_path, files)
    print(f"CBZ created at: {cbz_path}")

    # Delete downloaded images
    for path in files:
        path.unlink()