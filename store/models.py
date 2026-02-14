from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField(blank=True)
    rating = models.IntegerField(default=5)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"Order #{self.id}"

    @property
    def get_cart_total(self):
        # Calculates sum of all item totals in this order
        order_items = self.items.all()
        return sum([item.get_total for item in order_items])

    @property
    def get_cart_count(self):
        # Calculates total quantity of items in cart
        order_items = self.items.all()
        return sum([item.quantity for item in order_items])

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, related_name='items')
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name if self.product else 'Deleted Product'} (x{self.quantity})"

    @property
    def get_total(self):
        # Safety check: if product is deleted, total is 0
        if self.product:
            return self.product.price * self.quantity
        return 0