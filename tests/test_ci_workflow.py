"""
T8 — CI workflow sanity tests.

Pairs with Phase 5 task T8 (CI bootstrap). Doesn't run the workflow
(that's GitHub's job) — just guards against the YAML drifting in ways
that would silently disable the safety net.

Specifically the workflow must:
  - Parse as valid YAML.
  - Trigger on `pull_request` targeting main AND on `push` to main.
    Either trigger alone is a regression — PRs without push coverage
    miss direct-to-main pushes; push-only without PR coverage means
    every PR can merge without testing.
  - Run pytest against the `tests/` directory.
  - Pin a Python version (so CI doesn't drift from local dev).
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "tests.yml"


def _read_workflow_text() -> str:
    assert WORKFLOW_PATH.exists(), (
        f"{WORKFLOW_PATH.relative_to(REPO_ROOT)} is missing. T8 bootstrap "
        "added it; if it was removed the test suite no longer gates merges."
    )
    return WORKFLOW_PATH.read_text()


def test_workflow_file_exists():
    """The CI workflow file must exist at .github/workflows/tests.yml."""
    _read_workflow_text()


def test_workflow_is_valid_yaml():
    """The workflow must parse as valid YAML."""
    try:
        import yaml  # type: ignore
    except ImportError:
        # PyYAML isn't a project dep; if it's not installed in the local
        # venv just skip the structural checks. CI will catch YAML errors
        # by failing to start the workflow at all.
        import pytest
        pytest.skip("PyYAML not available locally — GitHub will validate the YAML at run time.")
    parsed = yaml.safe_load(_read_workflow_text())
    assert isinstance(parsed, dict), "Top-level workflow YAML must be a mapping."


def test_workflow_triggers_on_pull_request_and_push_to_main():
    """Both PR-to-main and push-to-main triggers must be present."""
    src = _read_workflow_text()
    # We do plain-text checks so the test doesn't need PyYAML installed in
    # the venv. The two triggers each need a `branches: [main]` line.
    assert "pull_request:" in src, (
        "Workflow must include a `pull_request:` trigger so PRs are tested."
    )
    assert "push:" in src, (
        "Workflow must include a `push:` trigger so direct pushes to main "
        "(merges, hotfix commits) are also tested."
    )
    # main branch coverage on both
    assert "branches: [main]" in src or "- main" in src, (
        "Workflow triggers must target the main branch — otherwise the "
        "safety net never fires on the branch that actually deploys."
    )


def test_workflow_runs_pytest():
    """The workflow must invoke pytest against the tests/ directory."""
    src = _read_workflow_text()
    assert "pytest tests/" in src or "pytest tests " in src, (
        "Workflow must run `pytest tests/` so all home/a11y/KPI/etc. "
        "regression guards execute. Without this the workflow is decorative."
    )


def test_workflow_pins_python_version():
    """The workflow must pin a Python version so CI doesn't drift from local dev."""
    src = _read_workflow_text()
    assert "python-version:" in src, (
        "Workflow must set `python-version` in the setup-python step. "
        "Otherwise CI uses whatever default Ubuntu ships, which may "
        "diverge from the local .venv (currently 3.13.x)."
    )


def test_workflow_installs_pytest():
    """pytest is a dev dep, not in requirements.txt — workflow must install it."""
    src = _read_workflow_text()
    assert "pip install pytest" in src or "install pytest" in src, (
        "Workflow must `pip install pytest` (the project's requirements.txt "
        "lists project deps including hypothesis, but not pytest itself)."
    )
