# Created: dylannguyen
from datetime import datetime
from typing import List
from pydantic import BaseModel

class ChatRequest(BaseModel):
    text: str

class ExtractedInfo(BaseModel):
    text: str
    facialExpression:str
    animation: str
    
class AgentResponse(BaseModel):
    messages: List[ExtractedInfo]

class MessageConversation(BaseModel):
    role: str
    content: str
    time: datetime # important for keeping track of the time of the message
    
class ChatMessageHistory(BaseModel):
    messages: List[MessageConversation]