# Code AST MCP Server (`code-ast-mcp`)

[![Model Context Protocol](https://img.shields.io/badge/MCP-Server-blue.svg)](https://modelcontextprotocol.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://python.org)
[![Smithery Server](https://img.shields.io/badge/Smithery-sameerbalouch758%2Fcode--ast--mcp-orange.svg)](https://smithery.ai/servers/sameerbalouch758/code-ast-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**`code-ast-mcp`** is an architectural Model Context Protocol (MCP) server built with Python's native Abstract Syntax Tree (`ast`) parser. It allows AI models (in Claude Desktop, Cursor, Antigravity, or custom MCP clients) to analyze local Python codebase structures, search symbol definitions, build dependency graphs, audit docstring coverage, and refactor code **without loading entire raw source files into LLM context windows**.

🔗 **Live Repository**: [https://github.com/m-sameerkhan/code-ast-mcp](https://github.com/m-sameerkhan/code-ast-mcp)  
🔗 **Smithery Registry**: [https://smithery.ai/servers/sameerbalouch758/code-ast-mcp](https://smithery.ai/servers/sameerbalouch758/code-ast-mcp)

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

## 🚀 Quickstart & Installation

### Option 1: Install via Smithery CLI
```bash
smithery mcp add sameerbalouch758/code-ast-mcp
```

---

### Option 2: Local Installation from Source

Clone the repository and install dependencies in editable mode:

```bash
git clone https://github.com/m-sameerkhan/code-ast-mcp.git
cd code-ast-mcp

# Create & activate virtual environment (or Conda)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install project and dependencies
pip install -r requirements.txt
pip install -e .
```

---

### Option 3: Package as an MCP Bundle (`.mcpb`)

For desktop clients that support MCP Bundles (like Claude Desktop):

```bash
# Install MCPB toolchain
npm install -g @anthropic-ai/mcpb

# Build bundle
mcpb pack . code-ast-mcp.mcpb
```

---

## 🧪 Testing Locally

### Run Unit Tests
```bash
pytest
```

### Test with MCP Inspector
Use the official MCP Inspector to interactively test tools and resources:
```bash
npx @modelcontextprotocol/inspector python -m code_ast_mcp.server
```

---

## ⚙️ Client Configuration

### Claude Desktop / Cursor / Antigravity Integration

Add `code-ast-mcp` to your client configuration file (`claude_desktop_config.json` or `mcp_config.json`):

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

*Note for Windows users: You can point `"command"` to your virtual environment or Conda Python path (e.g. `C:/Users/<Username>/.conda/envs/code-ast-mcp/python.exe` or `D:/my_mcp/.venv/Scripts/python.exe`).*

---

## 📦 Project Structure

```text
code-ast-mcp/
├── code_ast_mcp/          # Core package
│   ├── __init__.py        # Package exports
│   ├── analyzer.py        # Python AST parsing & static analysis engine
│   └── server.py          # FastMCP server definition & tool handlers
├── tests/                 # Test suite
│   └── test_analyzer.py   # Unit tests with pytest
├── manifest.json          # MCPB extension manifest
├── smithery.yaml          # Smithery registry configuration
├── Dockerfile             # Container image definition
├── pyproject.toml         # Packaging & metadata
└── requirements.txt       # Dependencies
```

---

## 📄 License
MIT License. Created by [m-sameerkhan](https://github.com/m-sameerkhan).
