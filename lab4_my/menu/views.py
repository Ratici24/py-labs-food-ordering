from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponseBadRequest
from . import data


def menu(request):
    categories = []
    for c in data.CATEGORIES:
        categories.append({
            **c,
            "dishes": [d for d in data.DISHES if d["category_id"] == c["id"]],
        })
    return render(request, "menu/menu.html", {"categories": categories})


def dish_detail(request, dish_id):
    dish = next((d for d in data.DISHES if d["id"] == dish_id), None)
    if not dish:
        return HttpResponseNotFound("Страву не знайдено")
    return render(request, "menu/dish_detail.html", {"dish": dish})


def orders(request):
    enriched = []
    for o in data.ORDERS:
        dish = next((d for d in data.DISHES if d["id"] == o["dish_id"]), None)
        enriched.append({**o, "dish_name": dish["name"] if dish else "-"})
    return render(request, "menu/orders.html", {"orders": enriched})


def place_order(request, dish_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    customer_name = request.POST.get("customer_name", "").strip()
    if not customer_name:
        return HttpResponseBadRequest("Введіть ім'я")
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except ValueError:
        return HttpResponseBadRequest("Некоректна кількість")
    if quantity < 1:
        return HttpResponseBadRequest("Кількість має бути ≥ 1")
    data.ORDERS.append({
        "id": len(data.ORDERS) + 1,
        "customer_name": customer_name,
        "dish_id": dish_id,
        "quantity": quantity,
        "status": "pending",
    })
    return redirect("menu:orders")
