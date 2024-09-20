from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity', 'warranty_period')
    list_filter = ('warranty_period',)
    search_fields = ('name', 'description')