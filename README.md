# Code AST MCP Server (`code-ast-mcp`)

[![Model Context Protocol](https://img.shields.io/badge/MCP-Server-blue.svg)](https://modelcontextprotocol.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://python.org)
[![Smithery Compatible](https://img.shields.io/badge/Smithery-Deployable-purple.svg)](https://smithery.ai)

**`code-ast-mcp`** is an architectural Model Context Protocol (MCP) server built with Python's native Abstract Syntax Tree (`ast`) parser. It allows AI models (in Claude Desktop, Cursor, Antigravity, or custom MCP clients) to analyze local Python codebase structures, search symbol definitions, build dependency graphs, audit docstring coverage, and refactor code **without loading entire raw source files into LLM context windows**.

---

## ⚡ Features & Capabilities

### 🛠️ Tools
1. **`analyze_file_ast(file_path: str)`**
   - Parses a `.py` file into a clean AST outline.
   - Extracts module docstring, line counts, imports, top-level functions, classes, methods, and variables.
2. **`find_class_methods(file_path: str, class_name: str)`**
   - Locates a class and returns method signatures, type annotations, line ranges, and docstrings.
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

### 1. Local Installation

Clone the repository and install dependencies in editable mode:

```bash
git clone https://github.com/your-username/code-ast-mcp.git
cd code-ast-mcp

# Create & activate Conda environment
conda create -n code-ast-mcp python=3.11 -y
conda activate code-ast-mcp

# Install project and dependencies
pip install -r requirements.txt
pip install -e .
```

### 2. Testing Locally

#### Run Unit Tests
```bash
pytest
```

#### Test with MCP Inspector
Use the official MCP Inspector to interactively test tools and resources:
```bash
npx @modelcontextprotocol/inspector python -m code_ast_mcp.server
```

---

## ⚙️ Client Configuration

### Claude Desktop / Antigravity Integration

Add `code-ast-mcp` to your client configuration file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "code-ast-mcp": {
      "command": "C:/Users/M.Sameer/.conda/envs/code-ast-mcp/python.exe",
      "args": [
        "-m",
        "code_ast_mcp.server"
      ],
      "cwd": "d:/my_mcp"
    }
  }
}
```

---

## 🌐 Deployment to Smithery / Marketplace

This MCP server includes `smithery.yaml` and `Dockerfile` for one-click deployment to **Smithery**:

1. Install Smithery CLI:
   ```bash
   npm install -g @smithery/cli
   ```
2. Deploy to Smithery:
   ```bash
   smithery deploy
   ```

---
