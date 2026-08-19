import json
from pathlib import Path
from starlette.responses import JSONResponse
from code_ast_mcp.server import mcp

# Create the FastMCP SSE ASGI application
app = mcp.sse_app()

SERVER_CARD_PATH = Path(__file__).parent.parent / ".well-known" / "mcp" / "server-card.json"


async def root_handler(request):
    return JSONResponse({
        "name": "code-ast-mcp",
        "version": "0.1.0",
        "status": "online",
        "transport": "SSE",
        "sse_endpoint": "/sse",
        "messages_endpoint": "/messages/"
    })


async def server_card_handler(request):
    if SERVER_CARD_PATH.exists():
        with open(SERVER_CARD_PATH, "r", encoding="utf-8") as f:
            card_data = json.load(f)
        return JSONResponse(card_data)
    return JSONResponse({"error": "server-card.json not found"}, status_code=404)


# Register routes on the Starlette ASGI application
app.add_route("/", root_handler, methods=["GET"])
app.add_route("/.well-known/mcp/server-card.json", server_card_handler, methods=["GET"])
