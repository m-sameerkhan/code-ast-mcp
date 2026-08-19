# Use official minimal Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml requirements.txt README.md ./
COPY code_ast_mcp/ ./code_ast_mcp/

# Install dependencies and package
RUN pip install --no-cache-dir .

# Command to launch the stdio MCP server
ENTRYPOINT ["python", "-m", "code_ast_mcp.server"]
