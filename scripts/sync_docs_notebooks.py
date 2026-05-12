from __future__ import annotations

import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_EXAMPLES_ROOT = REPO_ROOT / "docs" / "src" / "examples"


def reset_examples_root() -> None:
    shutil.rmtree(DOCS_EXAMPLES_ROOT / "bluebird-dt", ignore_errors=True)
    shutil.rmtree(DOCS_EXAMPLES_ROOT / "bluebird-gymnasium", ignore_errors=True)
    DOCS_EXAMPLES_ROOT.mkdir(parents=True, exist_ok=True)


def copy_tree(src: Path, dest: Path) -> None:
    shutil.copytree(src, dest)


def main() -> None:
    reset_examples_root()
    copy_tree(REPO_ROOT / "bluebird-dt" / "examples", DOCS_EXAMPLES_ROOT / "bluebird-dt")
    copy_tree(REPO_ROOT / "bluebird-gymnasium" / "examples", DOCS_EXAMPLES_ROOT / "bluebird-gymnasium")


if __name__ == "__main__":
    main()
