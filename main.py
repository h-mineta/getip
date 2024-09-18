#!/usr/bin/env python3

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(
    title="getip",
    version="1.0.0",
    redoc_url=None)

@app.get("/", responses={200: {"content": {"text/plain": {}, "application/json": None}}})
async def response_ip_text(request: Request):
    client_host = request.client.host
    return Response(content=client_host, media_type="text/plain")

@app.get("/json")
async def response_ip_json(request: Request):
    client_host = request.client.host
    return JSONResponse({"client_host": client_host})

if __name__ == '__main__':
    uvicorn.run(app=app)
