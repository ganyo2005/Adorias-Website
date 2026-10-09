from django.contrib import admin

from .models import SpecialOrder, ProductEnquiry


@admin.register(SpecialOrder)
class SpecialOrderAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "brand_model", "quantity", "created_at"]
    search_fields = ["name", "phone", "brand_model"]
    ordering = ["-created_at"]


@admin.register(ProductEnquiry)
class ProductEnquiryAdmin(admin.ModelAdmin):
    list_display = ["product_name", "product_sku", "created_at"]
    search_fields = ["product_name", "product_sku"]
    ordering = ["-created_at"]
