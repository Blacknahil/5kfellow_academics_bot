from __future__ import annotations

import logging
from pathlib import Path


def default_target() -> Path:
    # Import lazily to avoid adding a hard dependency at module load time,
    # but the canonical path is always the one defined in constants.
    try:
        from constants import TEMP_DOWNLOADS_DIR
        return TEMP_DOWNLOADS_DIR
    except ImportError:
        # Fallback when the module is run from the repo root directly.
        return Path(__file__).resolve().parents[1] / "temp_downloads"


def purge_all(target: Path, dry_run: bool = False) -> int:
    """Remove all entries inside `target` directory."""
    removed = 0

    if not target.exists():
        logging.info("Target directory does not exist: %s", target)
        return 0

    for entry in target.iterdir():
        try:
            if dry_run:
                logging.info("[dry-run] would remove: %s", entry)
                removed += 1
                continue

            if entry.is_file() or entry.is_symlink():
                entry.unlink()
                logging.info("Removed file: %s", entry)
            elif entry.is_dir():
                import shutil

                shutil.rmtree(entry)
                logging.info("Removed directory: %s", entry)
            removed += 1
        except Exception:
            logging.exception("Failed to remove %s", entry)

    logging.info("Purge complete — %d items removed from %s", removed, target)
    return removed


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Purge all files in temp_downloads (runs immediately)")
    parser.add_argument("--path", help="Directory to purge (default: repo/temp_downloads)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed, don't delete")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    target = Path(args.path) if args.path else default_target()

    try:
        # Run purge immediately by default when script is executed.
        removed = purge_all(target, args.dry_run)
        return 0 if removed >= 0 else 1
    except Exception:
        logging.exception("Unhandled error during purge")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
