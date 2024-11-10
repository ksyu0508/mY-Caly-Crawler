from pydantic import BaseModel

class ItemSchema(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

    class Config:
        orm_mode = True
