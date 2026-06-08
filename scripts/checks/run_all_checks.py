#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKS_DIR = ROOT / "scripts" / "checks"
GUARDS_DIR = ROOT / "scripts" / "guards"


def check_scripts() -> list[Path]:
    return sorted(
        path
        for path in CHECKS_DIR.glob("*_check.py")
        if path.name != Path(__file__).name
    )


def main() -> int:
    env = os.environ.copy()
    pythonpath_parts = [str(GUARDS_DIR)]
    if env.get("PYTHONPATH"):
        pythonpath_parts.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

    scripts = check_scripts()
    if not scripts:
        print("run_all_checks: no check scripts found")
        return 1

    for script in scripts:
        relative_script = script.relative_to(ROOT)
        print(f"run_all_checks: {relative_script}", flush=True)
        result = subprocess.run(
            [sys.executable, str(relative_script)],
            cwd=ROOT,
            env=env,
            check=False,
        )
        if result.returncode != 0:
            print(
                f"run_all_checks: FAILED {relative_script} exit={result.returncode}",
                flush=True,
            )
            return result.returncode

    print(f"run_all_checks: ok ({len(scripts)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
