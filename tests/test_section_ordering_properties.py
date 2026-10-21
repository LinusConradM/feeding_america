"""
Section ordering tests for the Executive Overview page.

Asserts the post-PR-#22 layout: page header and KPI cards first, then the
national-to-state narrative (State Lookup, National Trend, Geographic,
State Rankings), with Statistical Details last.
"""

import re

import pytest

VIEW_PATH = 'views/1_Executive_Overview.py'

EXPECTED_ORDER = [
    ('Page Header', r'^# ── Page Header'),
    ('KPI Cards', r'^# KPI Cards'),
    ('State Lookup', r'^# SECTION \d+(\.\d+)?: STATE LOOKUP'),
    ('National Trend', r'^# SECTION \d+(\.\d+)?: NATIONAL TREND'),
    ('Geographic Section', r'^# SECTION \d+(\.\d+)?: GEOGRAPHIC SECTION'),
    ('State Rankings', r'^# SECTION \d+(\.\d+)?: STATE RANKINGS'),
    ('Statistical Details', r'^# SECTION \d+(\.\d+)?: STATISTICAL DETAILS'),
]


@pytest.fixture(scope='module')
def source_code():
    with open(VIEW_PATH, 'r') as f:
        return f.read()


def _positions(source_code):
    positions = {}
    for name, pattern in EXPECTED_ORDER:
        matches = list(re.finditer(pattern, source_code, re.MULTILINE))
        assert len(matches) == 1, \
            f"Expected exactly one '{name}' marker in {VIEW_PATH}, found {len(matches)}"
        positions[name] = matches[0].start()
    return positions


def test_all_section_markers_present(source_code):
    _positions(source_code)


def test_sections_appear_in_expected_order(source_code):
    positions = _positions(source_code)
    actual_order = sorted(positions, key=positions.get)
    expected_order = [name for name, _ in EXPECTED_ORDER]
    assert actual_order == expected_order, \
        f"Sections out of order.\nExpected: {expected_order}\nActual: {actual_order}"


def test_statistical_details_is_last(source_code):
    positions = _positions(source_code)
    assert max(positions, key=positions.get) == 'Statistical Details'


def test_collapsible_sections_render_in_order(source_code):
    rankings = source_code.find('key="state_rankings"')
    stats = source_code.find('key="statistical_details"')
    assert rankings != -1 and stats != -1, \
        "State Rankings and Statistical Details must be collapsible sections"
    assert rankings < stats
