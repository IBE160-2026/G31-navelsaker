"""AD-1: MRP-kjernen er ren. ``rbe.mrp`` importerer bare standardbiblioteket og seg selv.

Testen leser importene med ``ast`` (uten å kjøre koden) og feiler med modulnavn og import.
"""

import ast
import sys
from pathlib import Path

import pytest

MRP_DIR = Path(__file__).resolve().parents[2] / "src" / "rbe" / "mrp"
CORE_PACKAGE = "rbe.mrp"

FORBIDDEN_MODULES = frozenset(
    {
        "rbe.db",
        "rbe.api",
        "rbe.fixture",
        "rbe.config",
        "fastapi",
        "sqlalchemy",
        "pydantic",
        "pydantic_settings",
        "os",
        "pathlib",
        "io",
        "sys",
        "socket",
        "http",
        "urllib",
        "subprocess",
        "shutil",
        "tempfile",
        "sqlite3",
        "time",
        "datetime",
        "random",
        "logging",
        "json",
        "builtins",
        "importlib",
        "glob",
        "pickle",
        "shelve",
        "zipfile",
        "ssl",
        "asyncio",
        "threading",
        "multiprocessing",
        "ctypes",
        "uuid",
        "secrets",
        "zoneinfo",
        "calendar",
    }
)
FORBIDDEN_CALLS = frozenset(
    {"open", "print", "input", "__import__", "eval", "exec", "compile", "breakpoint"}
)


def _matches(module: str, prefix: str) -> bool:
    return module == prefix or module.startswith(prefix + ".")


def _module_problem(module: str) -> str | None:
    """Gi grunnen til at en modul er forbudt i kjernen, eller None hvis den er tillatt."""
    if any(_matches(module, forbidden) for forbidden in FORBIDDEN_MODULES):
        return "forbudt"
    if _matches(module, CORE_PACKAGE):
        return None
    if _matches(module, "rbe"):
        return "utenfor rbe.mrp"
    if module.split(".")[0] not in sys.stdlib_module_names:
        return "ikke standardbiblioteket"
    return None


def _resolve_relative(module: str | None, level: int, package: str) -> str:
    parts = package.split(".")
    if level > len(parts):
        return "." * level + (module or "")
    base = parts[: len(parts) - level + 1]
    return ".".join([*base, module] if module else base)


def _violations(source: str, package: str = CORE_PACKAGE) -> list[str]:
    """Finn forbudte importer og kall i en kildetekst som ligger i ``package``."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if (problem := _module_problem(alias.name)) is not None:
                    found.append(f"import {alias.name} ({problem})")
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                module = _resolve_relative(node.module, node.level, package)
            else:
                module = node.module or ""
            shown = "." * node.level + (node.module or "")
            for alias in node.names:
                full = module if alias.name == "*" else f"{module}.{alias.name}"
                # «from rbe import mrp» er lov, mens «from os import path» ikke er det.
                problem = _module_problem(full)
                if problem is None and not _matches(full, CORE_PACKAGE):
                    problem = _module_problem(module)
                if problem is not None:
                    found.append(f"from {shown} import {alias.name} ({problem})")
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in FORBIDDEN_CALLS
        ):
            found.append(f"{node.func.id}() (forbudt kall)")
    return found


@pytest.mark.parametrize(
    "snippet",
    [
        "from dataclasses import dataclass\n",
        "from .types import Item\n",
        "from rbe.mrp.types import Item\n",
        "from . import types\n",
        "from rbe import mrp\n",
        "import collections.abc\n",
        "from typing import Literal\n",
    ],
)
def test_ad1_purity_check_allows(snippet: str) -> None:
    assert _violations(snippet) == []


@pytest.mark.parametrize(
    "snippet",
    [
        "import sqlalchemy\n",
        "from rbe.db import x\n",
        "import pathlib\n",
        "from datetime import date\n",
        'open("f")\n',
        'print("f")\n',
        "input()\n",
        "import os.path\n",
        "from os import path\n",
        "from rbe import db\n",
        "from .. import config\n",
        "from ..api import health\n",
        "import numpy\n",
        "import rbe.main\n",
        "import json as j\n",
        "import builtins\n",
        '__import__("os")\n',
        'eval("1")\n',
        "import importlib\n",
    ],
)
def test_ad1_purity_check_rejects(snippet: str) -> None:
    assert _violations(snippet) != []


def test_ad1_core_is_pure() -> None:
    files = sorted(MRP_DIR.rglob("*.py"))
    assert files, f"fant ingen moduler i {MRP_DIR}"
    offenders: dict[str, list[str]] = {}
    for path in files:
        relative = path.relative_to(MRP_DIR)
        package = ".".join([CORE_PACKAGE, *relative.parent.parts])
        hits = _violations(path.read_text(encoding="utf-8"), package)
        if hits:
            offenders[f"{package}.{relative.stem}"] = hits
    assert offenders == {}, f"MRP-kjernen er ikke ren: {offenders}"
