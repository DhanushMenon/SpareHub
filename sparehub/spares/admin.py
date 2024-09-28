from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock_quantity', 'warranty']  # Changed 'warranty_period' to 'warranty'
    list_filter = ['category', 'availability']  # Removed 'warranty_period' from list_filter
    search_fields = ['name', 'description']