# views.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from shop.models import Product
from .kart import Cart
from .serializers import CartSerializer

class CartViewSet(viewsets.ViewSet):
    """
    ViewSet for interacting with the cart.
    """
    def list(self, request):
        """ Get the cart contents (GET /api/cart) """
        cart = Cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """ Add a product to the cart (POST /api/cart/add) """
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = get_object_or_404(Product, id=product_id)
        
        cart = Cart(request)
        cart.add(product, quantity)
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        """ Remove a product from the cart (POST /api/cart/remove) """
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        cart = Cart(request)
        cart.remove(product)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put'])
    def update(self, request):
        """ Update the quantity of a product in the cart (PUT /api/cart/update) """
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({"detail": "Quantity is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, id=product_id)
        
        cart = Cart(request)
        cart.add(product, quantity, override_quantity=True)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """ Clear the cart (DELETE /api/cart) """
        cart = Cart(request)
        cart.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)
