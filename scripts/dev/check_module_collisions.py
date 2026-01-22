from __future__ import annotations

from pathlib import Path


def _find_collisions(src_root: Path) -> list[str]:
    """
    Detect sibling collisions like:
      foo.py AND foo/ existing in the same directory

    This is a deterministic Python import foot-gun.
    """
    errors: list[str] = []

    for d in [p for p in src_root.rglob("*") if p.is_dir()]:
        py_files = {p.stem for p in d.glob("*.py")}
        subdirs = {p.name for p in d.iterdir() if p.is_dir()}
        collisions = sorted(py_files.intersection(subdirs))
        for name in collisions:
            errors.append(f"{d.relative_to(src_root)}: {name}.py and {name}/")

    return errors


def _find_init_py(src_root: Path) -> list[str]:
    """
    Flag any init.py anywhere under src. Package init must be __init__.py.
    """
    hits = sorted(p.relative_to(src_root) for p in src_root.rglob("init.py"))
    return [str(h) for h in hits]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    src_root = repo_root / "src"
    if not src_root.exists():
        print(f"ERROR: expected src/ missing at {src_root}")
        return 2

    collision_errors = _find_collisions(src_root)
    init_hits = _find_init_py(src_root)

    if collision_errors:
        print("ERROR: module/package name collisions found under src/:")
        for e in collision_errors:
            print(f"  - {e}")

    if init_hits:
        print("ERROR: init.py files found under src/ (use __init__.py instead):")
        for h in init_hits:
            print(f"  - {h}")

    if collision_errors or init_hits:
        return 2

    print("ok: no module/package collisions and no init.py under src/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
