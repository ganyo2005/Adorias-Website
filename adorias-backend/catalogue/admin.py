from django.contrib import admin

from .models import Product


class HasPhotoFilter(admin.SimpleListFilter):
    title = "has local photo"
    parameter_name = "has_photo"

    def lookups(self, request, model_admin):
        return [("yes", "Has photo"), ("no", "Missing photo")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(images=[])
        if self.value() == "no":
            return queryset.filter(images=[])
        return queryset


class SourcingConfidenceFilter(admin.SimpleListFilter):
    """Buckets the free-text image_sourcing_status into the handful of
    confidence levels the research tool actually uses, instead of one
    filter option per unique (long) status string."""
    title = "image sourcing confidence"
    parameter_name = "sourcing_confidence"
    BUCKETS = ["VERIFIED", "BUSINESS RULE CONFIRMED", "CATEGORY CONFIRMED", "RESEARCH REQUIRED", "REVIEW"]

    def lookups(self, request, model_admin):
        return [(b, b.title()) for b in self.BUCKETS]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(image_sourcing_status__startswith=self.value())
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "brand", "category", "subcategory", "has_photo", "image_sourcing_status"]
    list_filter = ["category", HasPhotoFilter, SourcingConfidenceFilter, "original_category", "brand", "exact", "verified"]
    search_fields = ["sku", "name", "brand", "model", "description", "subcategory"]
    ordering = ["category", "brand", "name"]

    @admin.display(boolean=True, description="Has photo")
    def has_photo(self, obj):
        return bool(obj.images)
