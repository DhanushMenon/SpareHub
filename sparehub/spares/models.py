from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    is_customer = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    address = models.TextField(blank=True)
    zipcode = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"Customer: {self.user.username}"
    

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Add company-specific fields
    company_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    company_address = models.TextField(blank=True)
    registration_date = models.DateField(null=True, blank=True)

    
    def __str__(self):
        return f"Company: {self.company_name}"
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    warranty_period = models.PositiveIntegerField(help_text="Warranty period in months")
    is_available = models.BooleanField(default=True)
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True)

    def __str__(self):
        return self.name









