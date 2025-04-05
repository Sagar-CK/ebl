# Define a message schema for the API
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class Message(BaseModel):
    role: str
    content: str
    
class Focus(str, Enum):
    MUSCLE = "muscle"
    SKIN = "skin"
    POSTURE = "posture"
    HAIR = "hair"

class ChatRequest(BaseModel):
    session_id: str
    focus: Focus
    messages: List[Message]
    video_urls: Optional[List[str]] = None
    photo_urls: Optional[List[str]] = None
    