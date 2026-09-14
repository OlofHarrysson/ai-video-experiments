"""Workspace locations supplied by the calling app, never inferred from installation."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    root: Path

    def project(self, name):
        return self.root / "projects" / name

    @property
    def rife_python(self):
        return self.root / "work/rife-session/.venv/bin/python"

    @property
    def rife_script(self):
        return self.root / "interpolate.py"
