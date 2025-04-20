from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    CartViewSet,
    OrderViewSet,
    PaymentViewSet,
)

app_name = 'shop'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'payment', PaymentViewSet, basename='payment')
#router.register(r'payment', PaymentProcessViewSet, basename='payment')

urlpatterns = [
    path('api/', include(router.urls)),
]
