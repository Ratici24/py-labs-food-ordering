from django import forms
from .models import Dish, Order


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ["name", "price", "category"]

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Ціна повинна бути більше 0")
        return price

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError("Назва занадто коротка")
        return name


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "dish", "quantity"]

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty < 1:
            raise forms.ValidationError("Кількість повинна бути не менше 1")
        if qty > 100:
            raise forms.ValidationError("Максимум 100 за одне замовлення")
        return qty

    def clean_customer_name(self):
        name = self.cleaned_data["customer_name"].strip()
        if not name:
            raise forms.ValidationError("Введіть ім'я клієнта")
        return name
