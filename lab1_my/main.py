from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Food Ordering API",
    description="ІС «Замовлення їжі» — Лабораторна 1 (FastAPI + SQLAlchemy + SQLite)",
    version="1.0.0",
    openapi_tags=[
        {"name": "Pages", "description": "HTML сторінки застосунку"},
        {"name": "Dishes", "description": "CRUD операції для страв"},
        {"name": "Categories", "description": "Категорії меню"},
        {"name": "Orders", "description": "Замовлення клієнтів"},
    ],
)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse, tags=["Pages"])
def menu_page(request: Request, db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    dishes = db.query(models.Dish).all()
    return templates.TemplateResponse(
        request,
        "menu.html",
        {"categories": categories, "dishes": dishes},
    )


@app.get("/orders", response_class=HTMLResponse, tags=["Pages"])
def orders_page(request: Request, db: Session = Depends(get_db)):
    orders = db.query(models.Order).all()
    return templates.TemplateResponse(request, "orders.html", {"orders": orders})


@app.get("/admin", response_class=HTMLResponse, tags=["Pages"])
def admin_page(request: Request, db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    dishes = db.query(models.Dish).all()
    return templates.TemplateResponse(
        request,
        "admin.html",
        {"categories": categories, "dishes": dishes},
    )


@app.get("/api/dishes", response_model=list[schemas.DishOut], tags=["Dishes"])
def list_dishes_api(db: Session = Depends(get_db)):
    return db.query(models.Dish).all()


@app.post("/categories", tags=["Categories"])
def create_category(name: str = Form(...), db: Session = Depends(get_db)):
    db.add(models.Category(name=name))
    db.commit()
    return RedirectResponse("/admin", status_code=303)


@app.post("/dishes", tags=["Dishes"])
def create_dish(
    name: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    db: Session = Depends(get_db),
):
    db.add(models.Dish(name=name, price=price, category_id=category_id))
    db.commit()
    return RedirectResponse("/admin", status_code=303)


@app.post("/dishes/{dish_id}/update", tags=["Dishes"])
def update_dish(
    dish_id: int,
    name: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    db: Session = Depends(get_db),
):
    dish = db.query(models.Dish).filter(models.Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    dish.name = name
    dish.price = price
    dish.category_id = category_id
    db.commit()
    return RedirectResponse("/admin", status_code=303)


@app.post("/dishes/{dish_id}/delete", tags=["Dishes"])
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(models.Dish).filter(models.Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    db.delete(dish)
    db.commit()
    return RedirectResponse("/admin", status_code=303)

@app.post("/orders", tags=["Orders"])
def create_order(
    customer_name: str = Form(...),
    dish_id: int = Form(...),
    quantity: int = Form(1),
    db: Session = Depends(get_db),
):
    order = models.Order(customer_name=customer_name, dish_id=dish_id, quantity=quantity)
    db.add(order)
    db.commit()
    return RedirectResponse("/orders", status_code=303)


@app.post("/orders/{order_id}/status", tags=["Orders"])
def update_order_status(
    order_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    return RedirectResponse("/orders", status_code=303)