from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "dist" / "Resume Tailor.app"
INSTALLED_APP = Path.home() / "Applications" / "Resume Tailor.app"
PYTHON = shutil.which("python3") or "/usr/bin/python3"
PATH = os.environ.get("PATH", "") + ":/usr/local/bin:/opt/homebrew/bin"
SCRIPT = f'''
do shell script "export PATH={PATH}; cd {ROOT}; nohup {PYTHON} -m resume_tailor.ui > /tmp/resume-tailor-ui.log 2>&1 &"
delay 1
open location "http://127.0.0.1:8765"
'''.strip()

APP.parent.mkdir(exist_ok=True)
if APP.exists():
    shutil.rmtree(APP)
subprocess.run(["osacompile", "-o", str(APP), "-e", SCRIPT], check=True)
INSTALLED_APP.parent.mkdir(exist_ok=True)
if INSTALLED_APP.exists():
    shutil.rmtree(INSTALLED_APP)
shutil.copytree(APP, INSTALLED_APP)
print(APP)
print(INSTALLED_APP)
