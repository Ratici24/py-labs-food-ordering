from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class DishOut(BaseModel):
    id: int
    name: str
    price: float
    category_id: int

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    customer_name: str
    dish_id: int
    quantity: int
    status: str

    class Config:
        from_attributes = True