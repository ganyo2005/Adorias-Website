from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "sku", "brand", "name", "category", "original_category", "model",
            "specs", "key_specifications", "description", "compatibility", "use_cases",
            "battery", "charger", "power", "charger_power",
            "image", "images", "exact", "verified",
            "source_url", "official_product_page",
        ]


class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ["extra"]
