from django.urls import path
from . import views

urlpatterns = [
    path('jwks.json', views.jwks, name='jwks'),
]