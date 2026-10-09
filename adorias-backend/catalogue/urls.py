from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path("products/<str:sku>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("categories/", views.categories_view, name="categories"),
    path("catalogue.js", views.catalogue_js_view, name="catalogue-js"),
]
