from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

failures = 0
for module_name in ["tests.test_keywords", "tests.test_latex", "tests.test_ui"]:
    module = importlib.import_module(module_name)
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if not name.startswith("test_"):
            continue
        try:
            func()
            print(f"PASS {module_name}.{name}")
        except Exception as exc:  # noqa: BLE001 - tiny local runner
            failures += 1
            print(f"FAIL {module_name}.{name}: {exc}")

raise SystemExit(1 if failures else 0)
