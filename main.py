
import hashlib
import re

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def health():
    return {"status": "ok"}

@app.post("/")
@app.post("/mcp")
async def mcp(request: Request):
    body = await request.json()
    method = body.get("method")
    request_id = body.get("id")

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": body.get("params", {}).get(
                    "protocolVersion", "2025-03-26"
                ),
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "exam-challenge-server",
                    "version": "1.0.0"
                }
            }
        })

    if method == "notifications/initialized":
        return JSONResponse({}, status_code=202)

    if method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [{
                    "name": "solve_challenge",
                    "description": "Solve the current exam challenge",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }]
            }
        })

    if method == "tools/call":
        challenge = request.headers.get("X-Exam-Challenge", "")

        if not re.fullmatch(r"[0-9a-f]{32}", challenge):
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Missing or invalid X-Exam-Challenge header"
                }
            })

        params = body.get("params", {})
        if params.get("name") != "solve_challenge":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "Unknown tool"}
            })

        email = "24f2007761@ds.study.iitm.ac.in"
        digest = hashlib.sha256(
            f"{challenge}:{email}".encode()
        ).hexdigest()[:16]

        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{"type": "text", "text": digest}]
            }
        })

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32601,
            "message": f"Method not found: {method}"
        }
    })
