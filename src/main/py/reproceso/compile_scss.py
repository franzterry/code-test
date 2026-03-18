from __future__ import annotations

import os
from pathlib import Path


def _needs_rebuild(src: Path, dst: Path) -> bool:
    if not dst.exists():
        return True
    try:
        return src.stat().st_mtime > dst.stat().st_mtime
    except OSError:
        return True


def main() -> None:
    base = Path(__file__).resolve().parent
    src = base / "static" / "styles.scss"
    dst = base / "static" / "styles.css"

    if not src.exists():
        return
    if not _needs_rebuild(src, dst):
        return

    try:
        import sass  # type: ignore
    except Exception:
        # In case libsass isn't installed, do not block startup.
        return

    css = sass.compile(filename=str(src), output_style="compressed")
    banner = "/* Compiled from styles.scss */\n"
    dst.write_text(banner + css + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
