from django.urls import path
from . import views

app_name = "menu"

urlpatterns = [
    path("", views.menu, name="menu"),
    path("orders/", views.orders, name="orders"),
    path("order/new/", views.order_new, name="order_new"),
    path("dish/new/", views.dish_create, name="dish_create"),
    path("dish/<int:pk>/edit/", views.dish_update, name="dish_update"),
    path("dish/<int:pk>/delete/", views.dish_delete, name="dish_delete"),
    path("order/<int:pk>/status/", views.order_set_status, name="order_set_status"),
]
