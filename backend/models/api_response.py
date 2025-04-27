from pydantic import BaseModel
from typing import Optional


class APIResponse(BaseModel):
    code: int
    status: str
    message: str
    data: Optional[dict] = None
