"""Tests for problem statement implementation."""

import sys
from pathlib import Path
from io import StringIO

# Add examples to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "examples"))

from problem_statement_output import (
    generate_output,
    generate_as_dict,
    generate_as_list
)


def test_generate_output():
    """Test that generate_output produces correct format."""
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    generate_output()
    
    # Restore stdout
    sys.stdout = old_stdout
    
    # Verify output
    output = captured_output.getvalue()
    lines = output.strip().split('\n')
    
    assert len(lines) == 4, f"Expected 4 lines, got {len(lines)}"
    assert lines[0] == "1: 4-3-2-1", f"Line 1 mismatch: {lines[0]}"
    assert lines[1] == "2: 4", f"Line 2 mismatch: {lines[1]}"
    assert lines[2] == "3: 3", f"Line 3 mismatch: {lines[2]}"
    assert lines[3] == "4: 3", f"Line 4 mismatch: {lines[3]}"


def test_generate_as_dict():
    """Test dictionary representation."""
    result = generate_as_dict()
    
    assert isinstance(result, dict), "Should return a dictionary"
    assert len(result) == 4, f"Expected 4 items, got {len(result)}"
    assert result[1] == "4-3-2-1", f"Item 1 mismatch: {result[1]}"
    assert result[2] == 4, f"Item 2 mismatch: {result[2]}"
    assert result[3] == 3, f"Item 3 mismatch: {result[3]}"
    assert result[4] == 3, f"Item 4 mismatch: {result[4]}"


def test_generate_as_list():
    """Test list representation."""
    result = generate_as_list()
    
    assert isinstance(result, list), "Should return a list"
    assert len(result) == 4, f"Expected 4 items, got {len(result)}"
    assert result[0] == (1, "4-3-2-1"), f"Item 0 mismatch: {result[0]}"
    assert result[1] == (2, 4), f"Item 1 mismatch: {result[1]}"
    assert result[2] == (3, 3), f"Item 2 mismatch: {result[2]}"
    assert result[3] == (4, 3), f"Item 3 mismatch: {result[3]}"


def test_data_consistency():
    """Test that all representations contain the same data."""
    dict_result = generate_as_dict()
    list_result = generate_as_list()
    
    # Verify dict and list have same content
    for key, value in dict_result.items():
        list_item = next((item for item in list_result if item[0] == key), None)
        assert list_item is not None, f"Key {key} not found in list"
        assert list_item[1] == value, f"Value mismatch for key {key}"
