# Created by: dylannguyen
from pydantic import BaseModel


class SearchResponse(BaseModel):
    content: str
    created_at: str
    sourcefile: str