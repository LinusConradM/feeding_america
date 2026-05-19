"""
T4 — Home cache decorator presence tests.

Pairs with Phase 1 task 1.4: every home/nav file-loading helper that *claims*
to be cached must actually carry an @st.cache_data decorator. Commit 3854167
(Feb 26, 2026) silently stripped the decorators from _load_template and
_load_css while leaving their docstrings — and six inline `# OPTIMIZATION`
comments — claiming the caches were active. Q5 in HOME_REDESIGN_DECISIONS.md
resolved this as accidental; this test prevents silent recurrence.

The test parses each source file's AST and checks that the named functions
carry an @st.cache_data decorator (with or without keyword args).
"""
import ast
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent

CASES = [
    ("views/home.py", "_load_template"),
    ("views/home.py", "_load_css"),
    ("views/home.py", "_load_and_encode_image"),
    ("views/home.py", "_get_fi_ticker_html"),
    ("views/home.py", "_get_kpi_html"),
    ("utils/navigation.py", "_load_template"),
    ("utils/navigation.py", "_load_and_encode_image"),
    ("utils/navigation.py", "_get_fi_ticker_html"),
]


def _decorators_for(source_path: str, func_name: str):
    tree = ast.parse((REPO_ROOT / source_path).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return node.decorator_list
    pytest.fail(f"function {func_name} not found in {source_path}")


def _has_cache_data_decorator(decorators):
    for d in decorators:
        # @st.cache_data
        if isinstance(d, ast.Attribute) and d.attr == "cache_data":
            return True
        # @st.cache_data(...)
        if isinstance(d, ast.Call):
            f = d.func
            if isinstance(f, ast.Attribute) and f.attr == "cache_data":
                return True
            if isinstance(f, ast.Name) and f.id == "cache_data":
                return True
    return False


@pytest.mark.parametrize("source_path,func_name", CASES)
def test_function_has_cache_data_decorator(source_path, func_name):
    """Every cached helper must have @st.cache_data — prevents silent strip recurrence."""
    decorators = _decorators_for(source_path, func_name)
    assert _has_cache_data_decorator(decorators), (
        f"{source_path}::{func_name} is missing @st.cache_data. "
        "The docstring/comments claim it is cached but the decorator is gone. "
        "Q5 in HOME_REDESIGN_DECISIONS.md resolved this as accidental strip; "
        "the decorator must be present."
    )


def test_no_optimization_comment_lies():
    """
    Inline '# OPTIMIZATION:' comments that claim caching must be near an actual
    @st.cache_data decorator. The audit found six such comments still in place
    after the decorators were stripped — a documentation lie. Guard against it.
    """
    sources = [REPO_ROOT / "views" / "home.py", REPO_ROOT / "utils" / "navigation.py"]
    for src in sources:
        lines = src.read_text().splitlines()
        for i, line in enumerate(lines):
            if "# OPTIMIZATION" in line and ("cach" in line.lower() or "Template loading" in line):
                window = "\n".join(lines[max(0, i - 1) : i + 8])
                assert "@st.cache_data" in window, (
                    f"{src.name}:{i+1} claims caching in an OPTIMIZATION comment but "
                    f"no @st.cache_data decorator is present in the following ~8 lines:\n{window}"
                )
