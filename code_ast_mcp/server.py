import json
from pathlib import Path
from typing import List
from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent

from code_ast_mcp.analyzer import (
    analyze_file_ast as _analyze_file_ast,
    find_class_methods as _find_class_methods,
    find_symbol as _find_symbol,
    get_imports_graph as _get_imports_graph,
    find_missing_docstrings as _find_missing_docstrings,
)

# Initialize FastMCP Server
mcp = FastMCP(
    name="Code AST Inspector",
    instructions=(
        "An MCP server for analyzing Python codebase structure, extracting AST outlines, "
        "searching symbols, auditing docstring coverage, and mapping import dependencies."
    )
)


@mcp.tool()
def analyze_file_ast(file_path: str) -> str:
    """
    Parse a Python file using Python's AST parser and return a detailed outline 
    of its docstrings, imports, top-level classes, functions, variables, and line counts.
    
    :param file_path: Path to the Python (.py) file to analyze.
    """
    result = _analyze_file_ast(file_path)
    return json.dumps(result, indent=2)


@mcp.tool()
def find_class_methods(file_path: str, class_name: str) -> str:
    """
    Locate a specific class within a Python file and retrieve all its methods, 
    argument signatures, type annotations, line numbers, and docstrings.
    
    :param file_path: Path to the Python file containing the class.
    :param class_name: Name of the target class to inspect.
    """
    result = _find_class_methods(file_path, class_name)
    return json.dumps(result, indent=2)


@mcp.tool()
def find_symbol(target_dir: str, symbol_name: str) -> str:
    """
    Recursively search a directory or file for classes, functions, methods, or 
    variables matching the target symbol name.
    
    :param target_dir: Directory path or file path to search.
    :param symbol_name: Name or partial name of the symbol to search for.
    """
    result = _find_symbol(target_dir, symbol_name)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_imports_graph(target_dir: str) -> str:
    """
    Scan all Python files in a directory to build an import dependency graph 
    and output both a structured map and a Mermaid diagram definition.
    
    :param target_dir: Path to the directory containing Python files.
    """
    result = _get_imports_graph(target_dir)
    return json.dumps(result, indent=2)


@mcp.tool()
def find_missing_docstrings(target_dir: str, include_private: bool = False) -> str:
    """
    Audit Python files in a directory to identify modules, classes, and functions 
    that lack docstrings, calculating overall docstring coverage percentage.
    
    :param target_dir: Directory path to audit.
    :param include_private: Whether to include private functions/methods (starting with '_').
    """
    result = _find_missing_docstrings(target_dir, include_private)
    return json.dumps(result, indent=2)


@mcp.resource("codeast://stats")
def get_workspace_ast_stats() -> str:
    """Provide high-level AST statistics for the current workspace."""
    cwd = Path.cwd()
    imports_res = _get_imports_graph(str(cwd))
    docstrings_res = _find_missing_docstrings(str(cwd))
    
    stats = {
        "workspace_root": str(cwd),
        "total_python_files": imports_res.get("total_files_scanned", 0),
        "docstring_coverage": docstrings_res.get("coverage_percentage", "N/A"),
        "total_code_elements": docstrings_res.get("total_elements", 0),
        "missing_docstrings_count": docstrings_res.get("missing_count", 0),
    }
    return json.dumps(stats, indent=2)


@mcp.prompt()
def refactor_code_summary(file_path: str) -> List[PromptMessage]:
    """
    Generate a prompt guiding the LLM to inspect the AST outline of a Python file 
    and provide actionable code refactoring, architectural, and documentation advice.
    
    :param file_path: Path to the target Python file for refactoring review.
    """
    ast_json = analyze_file_ast(file_path)
    
    prompt_text = (
        f"You are an expert Python architect and code reviewer.\n"
        f"Below is the AST analysis outline for the file: '{file_path}'\n\n"
        f"```json\n{ast_json}\n```\n\n"
        f"Please analyze this file structure and provide:\n"
        f"1. **Architecture Overview**: Class and function responsibilities.\n"
        f"2. **Code Hygiene**: Missing docstrings or type hints.\n"
        f"3. **Refactoring Suggestions**: Single Responsibility Principle violations or design smells.\n"
        f"4. **Action Plan**: Step-by-step improvements to elevate code quality."
    )
    
    return [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text=prompt_text)
        )
    ]


def main():
    """Run the FastMCP server via standard IO transport."""
    mcp.run()


if __name__ == "__main__":
    main()
