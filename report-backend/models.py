from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserReport(BaseModel):
    user_id: int
    name: str
    email: str
    age: Optional[int]
    gender: Optional[str]
    country: Optional[str]
    total_signals: int
    first_signal: Optional[datetime]
    last_signal: Optional[datetime]
    days_with_data: int
    avg_amplitude: float
    avg_frequency: int
    avg_duration: int
    most_used_prosthesis: Optional[str]
    most_used_muscle: Optional[str]
    updated_at: datetime