# Code AST MCP Server (`code-ast-mcp`)

[![Model Context Protocol](https://img.shields.io/badge/MCP-Server-blue.svg)](https://modelcontextprotocol.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://python.org)
[![Glama MCP](https://glama.ai/mcp/servers/badge)](https://glama.ai/mcp/servers/m-sameerkhan/code-ast-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**`code-ast-mcp`** is an architectural Model Context Protocol (MCP) server built with Python's native Abstract Syntax Tree (`ast`) parser. It allows AI models (in Claude Desktop, Cursor, Antigravity, or custom MCP clients) to analyze Python codebase structures, search symbol definitions, build dependency graphs, audit docstring coverage, and refactor code **without loading entire raw source files into LLM context windows**.

🔗 **Live Repository**: [https://github.com/m-sameerkhan/code-ast-mcp](https://github.com/m-sameerkhan/code-ast-mcp)  
🔗 **Glama Registry**: [https://glama.ai/mcp/servers/m-sameerkhan/code-ast-mcp](https://glama.ai/mcp/servers/m-sameerkhan/code-ast-mcp)

---

## ⚡ Features & Capabilities

### 🛠️ Tools
1. **`analyze_file_ast(file_path: str)`**
   - Parses a `.py` file into a clean AST outline.
   - Extracts module docstrings, line counts, imports, top-level functions, classes, methods, and variables.
2. **`find_class_methods(file_path: str, class_name: str)`**
   - Locates a specific class and returns method signatures, type annotations, line ranges, and docstrings.
3. **`find_symbol(target_dir: str, symbol_name: str)`**
   - Recursively searches a directory for classes, functions, methods, or variable assignments matching `symbol_name`.
4. **`get_imports_graph(target_dir: str)`**
   - Scans Python files to build a dependency import map and outputs a **Mermaid diagram string**.
5. **`find_missing_docstrings(target_dir: str, include_private: bool = False)`**
   - Audits codebase docstrings and calculates overall docstring coverage percentage.

### 📝 Prompts
- **`refactor_code_summary(file_path: str)`**
  - Generates a structured prompt instructing the LLM to review the AST outline of a file and propose refactoring, design pattern improvements, and documentation fixes.

### 📊 Resources
- **`codeast://stats`**
  - Live JSON resource providing workspace statistics (total files scanned, docstring coverage %, missing item counts).

---

## 🚀 Deployment & Usage Modes

### Mode 1: Deploy via Glama MCP Registry

Deploy `code-ast-mcp` to the **[Glama MCP Registry](https://glama.ai/mcp/servers)** — Glama automatically clones your GitHub repo, builds it using the included `Dockerfile`, and hosts it with built-in OAuth 2.1, monitoring, and access control.

#### Steps:
1. Go to [glama.ai/mcp/servers](https://glama.ai/mcp/servers).
2. Click **"Add Server"**.
3. Authenticate with **GitHub OAuth** (you must have write access to the repo).
4. Submit the repository URL:
   ```text
   https://github.com/m-sameerkhan/code-ast-mcp
   ```
5. Glama will **auto-build** using the `Dockerfile` and verify MCP compliance.
6. Once the build succeeds, your server will be live on the Glama registry.

#### Registry URL:
```text
https://glama.ai/mcp/servers/m-sameerkhan/code-ast-mcp
```

> **Note**: No manual hosting required — Glama handles building, deployment, and verification automatically.

---

### Mode 2: Local Stdio MCP Server (Recommended for Local Codebases)

Best for inspecting local Python projects directly on your machine in Claude Desktop, Cursor, or Antigravity.

#### Installation:
```bash
git clone https://github.com/m-sameerkhan/code-ast-mcp.git
cd code-ast-mcp

# Virtual environment setup
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

#### Client Configuration (`claude_desktop_config.json` / `mcp_config.json`):
```json
{
  "mcpServers": {
    "code-ast-mcp": {
      "command": "python",
      "args": [
        "-m",
        "code_ast_mcp.server"
      ],
      "cwd": "/path/to/code-ast-mcp"
    }
  }
}
```

---

## 🧪 Testing Locally

### Run Unit Tests
```bash
pytest
```

### Test with MCP Inspector
```bash
npx @modelcontextprotocol/inspector python -m code_ast_mcp.server
```

---

## 📦 Project Structure

```text
code-ast-mcp/
├── code_ast_mcp/          # Core MCP package
│   ├── __init__.py        # Package exports
│   ├── analyzer.py        # Python AST parsing & static analysis engine
│   └── server.py          # FastMCP server definition & tool handlers
├── tests/                 # Test suite
│   └── test_analyzer.py   # Unit tests with pytest
├── Dockerfile             # Container image definition (used by Glama)
├── pyproject.toml         # Packaging & metadata
└── requirements.txt       # Dependencies
```

---

## 📄 License
MIT License. Created by [m-sameerkhan](https://github.com/m-sameerkhan).
