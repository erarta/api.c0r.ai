from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    telegram_id: int
    credits_remaining: int
    country: Optional[str] = None

class Payment(BaseModel):
    user_id: int
    amount: int
    description: str
    status: str 