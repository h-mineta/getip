#!/usr/bin/env python3

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(
    title="getip",
    version="1.0.0",
    redoc_url=None)

@app.get("/")
async def index(request: Request):
    client_host = request.client.host
    return JSONResponse({"client_host": client_host})

if __name__ == '__main__':
    uvicorn.run(app=app)
