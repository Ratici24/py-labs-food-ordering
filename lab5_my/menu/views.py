from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test

from .models import Category, Dish, Order
from .forms import DishForm, OrderForm


def is_admin(user):
    return user.is_authenticated and user.is_staff


def menu(request):
    categories = Category.objects.prefetch_related("dishes").all()
    return render(request, "menu/menu.html", {"categories": categories})


def orders(request):
    if request.user.is_authenticated and request.user.is_staff:
        qs = Order.objects.select_related("dish").all()
    elif request.user.is_authenticated:
        qs = Order.objects.select_related("dish").filter(
            customer_name=request.user.username
        )
    else:
        qs = Order.objects.none()
    return render(request, "menu/orders.html", {"orders": qs})


def order_new(request):
    initial = {}
    if request.user.is_authenticated:
        initial["customer_name"] = request.user.username
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("menu:orders")
    else:
        form = OrderForm(initial=initial)
    return render(request, "menu/order_form.html", {"form": form})


@user_passes_test(is_admin)
def dish_create(request):
    if request.method == "POST":
        form = DishForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("menu:menu")
    else:
        form = DishForm()
    return render(request, "menu/dish_form.html", {"form": form, "title": "Нова страва"})


@user_passes_test(is_admin)
def dish_update(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    if request.method == "POST":
        form = DishForm(request.POST, instance=dish)
        if form.is_valid():
            form.save()
            return redirect("menu:menu")
    else:
        form = DishForm(instance=dish)
    return render(request, "menu/dish_form.html", {"form": form, "title": "Редагувати"})


@user_passes_test(is_admin)
def dish_delete(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    if request.method == "POST":
        dish.delete()
        return redirect("menu:menu")
    return render(request, "menu/dish_confirm_delete.html", {"dish": dish})


@user_passes_test(is_admin)
def order_set_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
    return redirect("menu:orders")
