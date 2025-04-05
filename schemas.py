# Define a message schema for the API
from pydantic import BaseModel, Field
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
    photo_urls: Optional[List[str]] = None

class BasicChatRequest(BaseModel):
    messages: List[Message]

class Stage(BaseModel):
    title: str
    description: str
    tasks: List[str] = Field(..., description="Make thse tasks actionable, specific, and verifiable.")

class Plan(BaseModel):
    goal: str = Field(..., description="The main goal of the plan. Max 3 words.")
    motivation: str = Field(..., description="Motivation behind the goal. Max one sentence.")
    stages: List[Stage]

# Define pydantic model that is union of str or plan
class ResponsePlan(BaseModel):
    response: Optional[str] = Field(None, description="The response to the user on the plan creation.")
    plan: Optional[Plan] = None
    
class ChangePlanRequest(ChatRequest):
    plan: Plan