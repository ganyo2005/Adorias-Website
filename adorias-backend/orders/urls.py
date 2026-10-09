from django.urls import path

from . import views

urlpatterns = [
    path("special-order/", views.SpecialOrderView.as_view(), name="special-order"),
    path("product-enquiry/", views.ProductEnquiryView.as_view(), name="product-enquiry"),
]
