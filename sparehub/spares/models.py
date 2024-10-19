from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    user_type = models.CharField(max_length=10, choices=[
        ('CUSTOMER', 'Customer'),
        ('COMPANY', 'Company')
    ], default='CUSTOMER')

    objects = UserManager()
    def __str__(self):
        return self.username

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['username', 'email'], name='unique_user')
        ]

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='customer')
    address = models.TextField(blank=True)
    zipcode = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"Customer: {self.user.username}"

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    registration_number = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=100, unique=True)
    company_address = models.TextField()
    is_approved = models.BooleanField(default=False)
    car_makes = models.CharField(max_length=255, blank=True)
    part_categories = models.CharField(max_length=255, blank=True)
    manufacturing_type = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name_plural = "Companies"

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Any', 'Any'),
        ('BODY', 'Body'),
        ('ENGINE', 'Engine'),
        ('TRANSMISSION', 'Transmission'),
        ('AC', 'AC'),
        ('FUEL_SUPPLY', 'Fuel Supply'),
        ('BRAKE', 'Brake'),
        ('SUSPENSION', 'Suspension'),
        ('STEERING', 'Steering'),
        ('INTERIOR', 'Interior'),
        ('ELECTRONIC', 'Electronic Components'),
        ('EXHAUST', 'Exhaust System'),
        ('WHEELS', 'Wheels'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    car_makes = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]  # Ensure positive price
    )
    stock_quantity = models.PositiveIntegerField()
    warranty = models.CharField(max_length=100)  # This is probably the field you're using now
    availability = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=0)
    company_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['company', 'name']  # Ensure unique product names per company

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def total_price(self):
        return sum(item.subtotal() for item in self.cartitem_set.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def subtotal(self):
        return self.product.price * self.quantity

    def clean(self):
        if self.quantity > self.product.stock_quantity:
            raise ValidationError("Quantity cannot exceed available stock.")

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wishlist for {self.user.username}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)  # Make sure 'Product' is in quotes if it's defined later in the file
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order {self.order.id}"
