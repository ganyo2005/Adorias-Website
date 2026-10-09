from django.urls import path

from . import views

urlpatterns = [
    path("chat/", views.EfiaChatView.as_view(), name="efia-chat"),
]
