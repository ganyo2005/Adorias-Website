import json

from django.http import HttpResponse
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Product
from .serializers import ProductSerializer, ProductDetailSerializer
from .utils import all_products_as_dicts


class ProductListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.all()
        category = self.request.query_params.get("category")
        brand = self.request.query_params.get("brand")
        search = self.request.query_params.get("search")
        if category and category != "All":
            qs = qs.filter(category=category)
        if brand and brand != "All":
            qs = qs.filter(brand=brand)
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(name__icontains=search) | Q(brand__icontains=search) |
                Q(model__icontains=search) | Q(description__icontains=search)
            )
        return qs


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = "sku"


def catalogue_js_view(request):
    """Serves the full catalogue as a classic <script> exactly like the
    original static catalogue.js, but generated live from the database, so
    the frontend keeps its existing synchronous `window.ADORIAS_CATALOGUE`
    consumption pattern with zero changes while the data becomes real
    backend-owned state (editable via Django admin) instead of a hardcoded
    JS file.
    """
    body = "window.ADORIAS_CATALOGUE=" + json.dumps(all_products_as_dicts(), ensure_ascii=False) + ";"
    return HttpResponse(body, content_type="application/javascript")


@api_view(["GET"])
def categories_view(request):
    categories = list(
        Product.objects.order_by("category").values_list("category", flat=True).distinct()
    )
    brands = list(
        Product.objects.exclude(brand="").order_by("brand").values_list("brand", flat=True).distinct()
    )
    return Response({"categories": categories, "brands": brands})
