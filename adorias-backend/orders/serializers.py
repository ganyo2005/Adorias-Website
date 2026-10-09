from rest_framework import serializers

from .models import SpecialOrder, ProductEnquiry


class SpecialOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrder
        fields = ["id", "name", "phone", "brand_model", "quantity", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProductEnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductEnquiry
        fields = ["id", "product_sku", "product_name", "created_at"]
        read_only_fields = ["id", "created_at"]
