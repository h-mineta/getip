#!/usr/bin/env python3

from datetime import datetime, timedelta, timezone
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI(
    title="getip",
    version="1.0.0",
    redoc_url=None)

timezone_utc = timezone.utc
timezone_jst = timezone(timedelta(hours=9))

@app.get("/", responses={200: {"content": {"text/plain": {}, "application/json": None}}})
async def response_ip_text(request: Request):
    client_host = request.client.host # type: ignore
    return Response(content=client_host, media_type="text/plain")

@app.get("/json")
async def response_ip_json(request: Request):
    client_host = request.client.host # type: ignore
    datetime_now = datetime.now()
    return JSONResponse(
        {
            "client_host": client_host,
            "datetime_utc" : str(datetime_now.astimezone(timezone_utc)),
            "datetime_jst": str(datetime_now.astimezone(timezone_jst))
        }
    )

if __name__ == '__main__':
    uvicorn.run(app=app)
