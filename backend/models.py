from pydantic import BaseModel

class Preference(BaseModel):
    budget: float
    destination: str
    duration: int
    travel_style: str
    shopping_interest: str