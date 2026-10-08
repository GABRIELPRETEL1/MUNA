from django.urls import path
from .views import dashboard, checkout

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('checkout/', checkout, name='checkout'),
]
