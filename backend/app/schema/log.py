from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LogModel(BaseModel):
    action_date: datetime
    path_name: str
    method: str
    ip: str
    status_response: int
    response: str
    request_body: Optional[str]
    request_query: Optional[str]
    description: Optional[str]
    duration: float