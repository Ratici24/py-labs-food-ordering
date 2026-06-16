from django.urls import path
from . import views

app_name = "menu"

urlpatterns = [
    path("", views.menu, name="menu"),
    path("dish/<int:dish_id>/", views.dish_detail, name="dish_detail"),
    path("orders/", views.orders, name="orders"),
    path("order/new/<int:dish_id>/", views.place_order, name="place_order"),
]
