from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class FAQAnswer(BaseModel):
    answer: str = Field(min_length=1)
    citations: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)

class Requisites(BaseModel):
    recipient_name: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    account: Optional[str] = None
    bank_name: Optional[str] = None
    bik: Optional[str] = None
    correspondent_account: Optional[str] = None
    comment: Optional[str] = None

class ComplaintReply(BaseModel):
    category: Literal['fraud','card','transfer','service','other']
    escalation_needed: bool
    response_text: str
    ticket_tags: List[str] = []

class PaymentStatus(BaseModel):
    found: bool
    status: Literal['pending','completed','rejected','unknown']
    amount: float
    currency: str
    timestamp: str
    advice: str
