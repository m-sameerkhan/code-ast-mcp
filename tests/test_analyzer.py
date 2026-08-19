import json
import pytest
from pathlib import Path
from code_ast_mcp.analyzer import (
    analyze_file_ast,
    find_class_methods,
    find_symbol,
    get_imports_graph,
    find_missing_docstrings,
)
from code_ast_mcp.server import (
    analyze_file_ast as tool_analyze_ast,
    find_class_methods as tool_find_methods,
    find_symbol as tool_find_symbol,
    get_imports_graph as tool_get_graph,
    find_missing_docstrings as tool_find_missing,
)


@pytest.fixture
def sample_python_file(tmp_path):
    code = '''"""Sample module docstring."""
import os
from math import sqrt

GLOBAL_VAR = 42

def sample_function(x: int) -> int:
    """Sample function docstring."""
    return x * 2

class Calculator:
    """Calculator class docstring."""
    def __init__(self, value: int = 0):
        self.value = value
        
    def add(self, amount: int) -> int:
        """Add amount to value."""
        self.value += amount
        return self.value
        
    def _internal_helper(self):
        pass
'''
    file_path = tmp_path / "sample.py"
    file_path.write_text(code, encoding="utf-8")
    return file_path


def test_analyze_file_ast(sample_python_file):
    res = analyze_file_ast(str(sample_python_file))
    assert "error" not in res
    assert res["docstring"] == "Sample module docstring."
    assert len(res["classes"]) == 1
    assert res["classes"][0]["name"] == "Calculator"
    assert len(res["functions"]) == 1
    assert res["functions"][0]["name"] == "sample_function"
    assert len(res["imports"]) == 2


def test_find_class_methods(sample_python_file):
    res = find_class_methods(str(sample_python_file), "Calculator")
    assert "error" not in res
    assert res["class_name"] == "Calculator"
    assert len(res["methods"]) == 3
    method_names = [m["name"] for m in res["methods"]]
    assert "add" in method_names
    assert "__init__" in method_names


def test_find_symbol(sample_python_file):
    res = find_symbol(str(sample_python_file), "add")
    assert res["total_matches"] >= 1
    symbols = [m["symbol"] for m in res["matches"]]
    assert "add" in symbols


def test_get_imports_graph(sample_python_file):
    res = get_imports_graph(str(sample_python_file.parent))
    assert res["total_files_scanned"] == 1
    assert "graph TD" in res["mermaid_graph"]


def test_find_missing_docstrings(sample_python_file):
    res = find_missing_docstrings(str(sample_python_file.parent), include_private=True)
    assert res["missing_count"] >= 1
    missing_names = [item["name"] for item in res["missing_items"]]
    assert "_internal_helper" in missing_names


def test_mcp_tools_format(sample_python_file):
    ast_json_str = tool_analyze_ast(str(sample_python_file))
    data = json.loads(ast_json_str)
    assert data["docstring"] == "Sample module docstring."

    methods_json_str = tool_find_methods(str(sample_python_file), "Calculator")
    data_methods = json.loads(methods_json_str)
    assert data_methods["class_name"] == "Calculator"

    symbols_json_str = tool_find_symbol(str(sample_python_file), "Calculator")
    data_symbols = json.loads(symbols_json_str)
    assert data_symbols["total_matches"] == 1
