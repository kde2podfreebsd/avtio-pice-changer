from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(
    title='TG WebApp',
    docs_url='/api/docs',
    redoc_url='/api/doc',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Content(BaseModel):
    call: Optional[Dict[str, Any]] = None
    image: Optional[Dict[str, Any]] = None
    item: Optional[Dict[str, Any]] = None
    link: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    text: Optional[str] = None

class WebhookData(BaseModel):
    author_id: int
    chat_id: str
    chat_type: str
    content: Content
    created: int
    id: str
    item_id: int
    read: int
    type: str
    user_id: int

@app.post("/webhook")
async def webhook(data: WebhookData):
    print(f"Received data: {data}")
    return {"status": "success"}