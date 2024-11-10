# app/routers/example_router.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@router.post("/items/")
async def create_item(item: Item):
    return {"item": item}
