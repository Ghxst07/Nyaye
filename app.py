from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict

from core.flow import handle_message
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import json
from core.sessions import sessions
from fastapi.middleware.cors import CORSMiddleware

import os

API_KEY = os.getenv("HONEYPOT_API_KEY")

if not API_KEY:
    raise Exception("HONEYPOT_API_KEY not set")  


app = FastAPI(title="Agentic Honeypot API")
@app.middleware("http")
async def log_raw_request(request, call_next):
    body = await request.body()
    print(f"RAW BODY: {body.decode('utf-8')}")
    
    request._body = body  # so FastAPI can still read it
    return await call_next(request)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Get the raw body to see what GUVI actually sent
    body = await request.body()
    
    print("\n--- DEBUG: INCOMING FAILURE ---")
    print(f"URL: {request.url}")
    print(f"Body received: {body.decode('utf-8')}")
    print("Validation Errors:")
    # Print each specific error (e.g., 'missing field: sessionId')
    print(json.dumps(exc.errors(), indent=2))
    print("-------------------------------\n")
    
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body.decode('utf-8')},
    )


class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

    class Config:
        extra = "allow"


class ConversationItem(BaseModel):
    sender: str
    text: str
    timestamp: int

    class Config:
        extra = "allow"


class Metadata(BaseModel):
    channel: Optional[str]
    language: Optional[str]
    locale: Optional[str]

    class Config:
        extra = "allow"


class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: Optional[List[ConversationItem]] = None
    metadata: Optional[Metadata] = None

    class Config:
        extra = "allow"
        allow_population_by_field_name = True


class HoneypotResponse(BaseModel):
    status: str
    reply: str

    class Config:
        extra = "allow"



@app.post("/honeypot", response_model=HoneypotResponse)
def honeypot_endpoint(
    payload: HoneypotRequest,
    x_api_key: str = Header(...)
):
    
    print("REQUEST RECEIVED")

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    session_id = payload.sessionId
    incoming_text = payload.message.text


    reply, stop_flag = handle_message(session_id, incoming_text)


    print("SESSION:", session_id)
    print("STOP FLAG:", stop_flag)
    print("EXTRACTED:", sessions[session_id].extracted)


    return {
        "status": "success",
        "reply": reply
    }
@app.post("/honeypot/", response_model=HoneypotResponse, include_in_schema=False)
def honeypot_slash_endpoint(
    payload: HoneypotRequest, 
    x_api_key: str = Header(...)):
    return honeypot_endpoint(payload, x_api_key)