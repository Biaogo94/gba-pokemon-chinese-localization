#!/usr/bin/env python3
"""Standalone entry point for the guarded source injector."""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_ROOT / "scripts"))

from tools.i18n.injector import *  # noqa: F401,F403,E402
from tools.i18n.injector import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
