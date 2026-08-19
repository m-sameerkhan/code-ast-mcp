import ast
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def _get_arg_annotation(arg: ast.arg) -> str:
    """Format argument type annotation if available."""
    if arg.annotation:
        try:
            return ast.unparse(arg.annotation)
        except Exception:
            return "Any"
    return "Any"


def _get_signature(node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> str:
    """Extract argument signature formatted as a string."""
    args_list = []
    for arg in node.args.args:
        ann = _get_arg_annotation(arg)
        args_list.append(f"{arg.arg}: {ann}")
    
    if node.args.vararg:
        args_list.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg:
        args_list.append(f"**{node.args.kwarg.arg}")
        
    return_ann = ""
    if node.returns:
        try:
            return_ann = f" -> {ast.unparse(node.returns)}"
        except Exception:
            pass
            
    return f"({', '.join(args_list)}){return_ann}"


def analyze_file_ast(file_path: str) -> Dict[str, Any]:
    """Parse a single Python file into a structured AST outline."""
    path = Path(file_path).resolve()
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    if not path.is_file():
        return {"error": f"Path is not a file: {file_path}"}
        
    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(path))
    except Exception as e:
        return {"error": f"Failed to parse Python file: {str(e)}"}
        
    total_lines = len(content.splitlines())
    module_doc = ast.get_docstring(tree) or ""
    
    imports = []
    classes = []
    functions = []
    variables = []
    
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"type": "import", "name": alias.name, "as": alias.asname})
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                imports.append({"type": "from_import", "module": mod, "name": alias.name, "as": alias.asname})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({
                "name": node.name,
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "signature": _get_signature(node),
                "line_start": node.lineno,
                "line_end": getattr(node, "end_lineno", node.lineno),
                "docstring": ast.get_docstring(node) or "",
                "decorators": [ast.unparse(d) for d in node.decorator_list if hasattr(ast, "unparse")]
            })
        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append({
                        "name": item.name,
                        "is_async": isinstance(item, ast.AsyncFunctionDef),
                        "signature": _get_signature(item),
                        "line_start": item.lineno,
                        "line_end": getattr(item, "end_lineno", item.lineno),
                        "docstring": ast.get_docstring(item) or "",
                    })
            classes.append({
                "name": node.name,
                "bases": [ast.unparse(b) for b in node.bases if hasattr(ast, "unparse")],
                "line_start": node.lineno,
                "line_end": getattr(node, "end_lineno", node.lineno),
                "docstring": ast.get_docstring(node) or "",
                "method_count": len(methods),
                "methods": methods
            })
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.append({"name": target.id, "line": node.lineno})
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                variables.append({
                    "name": node.target.id,
                    "type": ast.unparse(node.annotation) if hasattr(ast, "unparse") else "",
                    "line": node.lineno
                })

    return {
        "file_path": str(path),
        "total_lines": total_lines,
        "docstring": module_doc,
        "imports": imports,
        "classes": classes,
        "functions": functions,
        "variables": variables
    }


def find_class_methods(file_path: str, class_name: str) -> Dict[str, Any]:
    """Find a specific class in a file and list all its methods with details."""
    result = analyze_file_ast(file_path)
    if "error" in result:
        return result
        
    matching_class = None
    for cls in result.get("classes", []):
        if cls["name"].lower() == class_name.lower():
            matching_class = cls
            break
            
    if not matching_class:
        available = [c["name"] for c in result.get("classes", [])]
        return {
            "error": f"Class '{class_name}' not found in {file_path}.",
            "available_classes": available
        }
        
    return {
        "file_path": result["file_path"],
        "class_name": matching_class["name"],
        "docstring": matching_class["docstring"],
        "bases": matching_class["bases"],
        "line_start": matching_class["line_start"],
        "line_end": matching_class["line_end"],
        "methods": matching_class["methods"]
    }


def find_symbol(target_dir: str, symbol_name: str) -> Dict[str, Any]:
    """Recursively search for functions, classes, methods, or variables matching symbol_name."""
    base_path = Path(target_dir).resolve()
    if not base_path.exists():
        return {"error": f"Directory not found: {target_dir}"}
        
    matches = []
    search_lower = symbol_name.lower()
    
    ignore_dirs = {".venv", "venv", "__pycache__", ".git", "build", "dist", ".egg-info"}
    
    python_files = []
    if base_path.is_file() and base_path.suffix == ".py":
        python_files.append(base_path)
    else:
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)
                    
    for p in python_files:
        try:
            content = p.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(p))
        except Exception:
            continue
            
        rel_path = str(p.relative_to(base_path)) if base_path.is_dir() else str(p)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if search_lower in node.name.lower():
                    matches.append({
                        "symbol": node.name,
                        "kind": "function" if not getattr(node, "_is_method", False) else "method",
                        "file": rel_path,
                        "full_path": str(p),
                        "line": node.lineno,
                        "signature": _get_signature(node),
                        "docstring": (ast.get_docstring(node) or "")[:100]
                    })
            elif isinstance(node, ast.ClassDef):
                if search_lower in node.name.lower():
                    matches.append({
                        "symbol": node.name,
                        "kind": "class",
                        "file": rel_path,
                        "full_path": str(p),
                        "line": node.lineno,
                        "bases": [ast.unparse(b) for b in node.bases if hasattr(ast, "unparse")],
                        "docstring": (ast.get_docstring(node) or "")[:100]
                    })
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        setattr(item, "_is_method", True)

    return {
        "target_dir": str(base_path),
        "query": symbol_name,
        "total_matches": len(matches),
        "matches": matches
    }


def get_imports_graph(target_dir: str) -> Dict[str, Any]:
    """Generate a dependency import graph across all Python files in target_dir."""
    base_path = Path(target_dir).resolve()
    if not base_path.exists():
        return {"error": f"Directory not found: {target_dir}"}
        
    ignore_dirs = {".venv", "venv", "__pycache__", ".git", "build", "dist"}
    file_imports: Dict[str, List[str]] = {}
    
    python_files = []
    if base_path.is_file() and base_path.suffix == ".py":
        python_files.append(base_path)
    else:
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

    for p in python_files:
        rel_path = str(p.relative_to(base_path)) if base_path.is_dir() else p.name
        try:
            content = p.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(p))
        except Exception:
            continue
            
        imported_mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_mods.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_mods.add(node.module.split('.')[0])
                    
        file_imports[rel_path] = sorted(list(imported_mods))

    mermaid_lines = ["graph TD"]
    for file_name, mods in file_imports.items():
        clean_file_id = file_name.replace("\\", "_").replace("/", "_").replace(".", "_").replace("-", "_")
        mermaid_lines.append(f'    {clean_file_id}["{file_name}"]')
        for mod in mods:
            clean_mod_id = f"mod_{mod}".replace("-", "_")
            mermaid_lines.append(f'    {clean_file_id} --> {clean_mod_id}["{mod}"]')

    return {
        "target_dir": str(base_path),
        "total_files_scanned": len(python_files),
        "imports_map": file_imports,
        "mermaid_graph": "\n".join(mermaid_lines)
    }


def find_missing_docstrings(target_dir: str, include_private: bool = False) -> Dict[str, Any]:
    """Identify modules, classes, and functions missing docstrings."""
    base_path = Path(target_dir).resolve()
    if not base_path.exists():
        return {"error": f"Directory not found: {target_dir}"}
        
    ignore_dirs = {".venv", "venv", "__pycache__", ".git", "build", "dist"}
    missing_items = []
    total_elements = 0
    documented_elements = 0

    python_files = []
    if base_path.is_file() and base_path.suffix == ".py":
        python_files.append(base_path)
    else:
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

    for p in python_files:
        rel_path = str(p.relative_to(base_path)) if base_path.is_dir() else p.name
        try:
            content = p.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(p))
        except Exception:
            continue
            
        total_elements += 1
        mod_doc = ast.get_docstring(tree)
        if mod_doc:
            documented_elements += 1
        else:
            missing_items.append({
                "file": rel_path,
                "kind": "module",
                "name": rel_path,
                "line": 1
            })

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = node.name
                if not include_private and name.startswith("_") and not name.startswith("__"):
                    continue
                    
                total_elements += 1
                doc = ast.get_docstring(node)
                if doc:
                    documented_elements += 1
                else:
                    kind = "class" if isinstance(node, ast.ClassDef) else "function"
                    missing_items.append({
                        "file": rel_path,
                        "kind": kind,
                        "name": name,
                        "line": node.lineno
                    })

    doc_percentage = round((documented_elements / total_elements * 100), 2) if total_elements > 0 else 100.0

    return {
        "target_dir": str(base_path),
        "total_elements": total_elements,
        "documented_elements": documented_elements,
        "coverage_percentage": f"{doc_percentage}%",
        "missing_count": len(missing_items),
        "missing_items": missing_items
    }
