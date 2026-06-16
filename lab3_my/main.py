from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from database import categories, dishes, orders
from datetime import datetime


app = FastAPI(
    title="Food Ordering API (MongoDB)",
    description="ІС «Замовлення їжі» — Лабораторна 3 (FastAPI + pymongo + MongoDB)",
    version="3.0.0",
    openapi_tags=[
        {"name": "Pages", "description": "HTML сторінки застосунку"},
        {"name": "Dishes", "description": "CRUD операції для страв"},
        {"name": "Categories", "description": "Категорії меню"},
        {"name": "Orders", "description": "Замовлення з вкладеним масивом items"},
        {"name": "Stats", "description": "MongoDB aggregation pipeline"},
    ],
)
templates = Jinja2Templates(directory="templates")


def _to_oid(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid id")


def _dish_view(d):
    return {
        "id": str(d["_id"]),
        "name": d["name"],
        "price": d["price"],
        "category": d.get("category", ""),
    }


def _category_view(c):
    return {"id": str(c["_id"]), "name": c["name"]}


@app.get("/", response_class=HTMLResponse, tags=["Pages"])
def menu_page(request: Request):
    all_dishes = [_dish_view(d) for d in dishes.find()]
    all_cats = [_category_view(c) for c in categories.find()]
    for c in all_cats:
        c["dishes"] = [d for d in all_dishes if d["category"] == c["name"]]
    return templates.TemplateResponse(
        request, "menu.html",
        {"categories": all_cats, "dishes": all_dishes},
    )


@app.get("/admin", response_class=HTMLResponse, tags=["Pages"])
def admin_page(request: Request):
    all_dishes = [_dish_view(d) for d in dishes.find()]
    all_cats = [_category_view(c) for c in categories.find()]
    return templates.TemplateResponse(
        request, "admin.html",
        {"dishes": all_dishes, "categories": all_cats},
    )


@app.get("/orders", response_class=HTMLResponse, tags=["Pages"])
def orders_page(request: Request):
    all_orders = []
    for o in orders.find():
        item_lines = []
        for it in o.get("items", []):
            try:
                d = dishes.find_one({"_id": ObjectId(it["dish_id"])})
                if d:
                    item_lines.append(f"{d['name']} × {it['qty']}")
            except InvalidId:
                continue
        all_orders.append({
            "id": str(o["_id"]),
            "customer_name": o["customer_name"],
            "items_text": ", ".join(item_lines),
            "status": o.get("status", "pending"),
        })
    return templates.TemplateResponse(
        request, "orders.html",
        {"orders": all_orders},
    )

@app.post("/categories", tags=["Categories"])
def create_category(name: str = Form(...)):
    categories.insert_one({"name": name})
    return RedirectResponse("/admin", status_code=303)


@app.post("/dishes", tags=["Dishes"])
def create_dish(
    name: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
):
    dishes.insert_one({"name": name, "price": price, "category": category})
    return RedirectResponse("/admin", status_code=303)


@app.post("/dishes/{dish_id}/update", tags=["Dishes"])
def update_dish(
    dish_id: str,
    name: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
):
    result = dishes.update_one(
        {"_id": _to_oid(dish_id)},
        {"$set": {"name": name, "price": price, "category": category}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    return RedirectResponse("/admin", status_code=303)


@app.post("/dishes/{dish_id}/delete", tags=["Dishes"])
def delete_dish(dish_id: str):
    result = dishes.delete_one({"_id": _to_oid(dish_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    return RedirectResponse("/admin", status_code=303)

@app.post("/orders", tags=["Orders"])
def create_order(
    customer_name: str = Form(...),
    dish_id: str = Form(...),
    quantity: int = Form(1),
):
    orders.insert_one({
        "customer_name": customer_name,
        "items": [{"dish_id": dish_id, "qty": quantity}],
        "status": "pending",
        "created_at": datetime.utcnow(),
    })
    return RedirectResponse("/orders", status_code=303)


@app.post("/orders/{order_id}/status", tags=["Orders"])
def update_order_status(order_id: str, status: str = Form(...)):
    result = orders.update_one(
        {"_id": _to_oid(order_id)},
        {"$set": {"status": status}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return RedirectResponse("/orders", status_code=303)

@app.get("/stats", response_class=HTMLResponse, tags=["Stats"])
def stats_page(request: Request):
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {"_id": "$items.dish_id", "total": {"$sum": "$items.qty"}}},
        {"$sort": {"total": -1}},
        {"$limit": 5},
    ]
    rows = []
    for r in orders.aggregate(pipeline):
        try:
            d = dishes.find_one({"_id": ObjectId(r["_id"])})
            if d:
                rows.append((d["name"], r["total"]))
        except InvalidId:
            continue
    return templates.TemplateResponse(
        request, "stats.html", {"rows": rows},
    )
