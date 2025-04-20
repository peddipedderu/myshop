# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

app_name = 'kart'

# Create a router and register the CartViewSet
router = DefaultRouter()
router.register(r'kart', CartViewSet, basename='kart')

# Include the cart URLs into the API routing
urlpatterns = [
    path('api/', include(router.urls)),
]
