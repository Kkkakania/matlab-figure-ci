"""Gallery output checks."""

from __future__ import annotations

from pathlib import Path

from .result import GalleryItem, GalleryResults


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def run_gallery_check(root: str | Path, config: dict) -> GalleryResults:
    root_path = Path(root).resolve()
    gallery_config = config.get("gallery", {})
    gallery_path = root_path / str(gallery_config.get("path", "gallery"))
    allowed = set(gallery_config.get("allowed_extensions", [".png", ".svg", ".pdf"]))
    min_size = int(gallery_config.get("min_size_bytes", 1024))
    expected = list(gallery_config.get("expected", []))
    result = GalleryResults()

    if not gallery_path.exists():
        result.items.append(GalleryItem("error", _rel(root_path, gallery_path), "gallery directory missing"))
        return result

    for name in expected:
        path = gallery_path / name
        rel = _rel(root_path, path)
        suffix = path.suffix.lower()
        if suffix not in allowed:
            result.items.append(GalleryItem("warning", rel, f"unexpected extension {suffix}"))
            continue
        if not path.exists():
            result.items.append(GalleryItem("error", rel, "missing expected gallery file"))
            continue
        size = path.stat().st_size
        if size == 0:
            result.items.append(GalleryItem("error", rel, "empty gallery file"))
            continue
        if size < min_size:
            result.items.append(GalleryItem("error", rel, f"gallery file smaller than {min_size} bytes"))
            continue
        result.items.append(GalleryItem("ok", rel, "present"))

    return result
