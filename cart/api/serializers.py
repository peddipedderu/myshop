# serializers.py
from rest_framework import serializers
from .kart import Cart
from shop.models import Product
from decimal import Decimal

class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_price'] = Decimal(instance['price']) * instance['quantity']
        return representation


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def to_representation(self, instance):
        items = [item for item in instance]
        total_price = sum(Decimal(item['price']) * item['quantity'] for item in items)
        return {
            'items': items,
            'total_price': total_price,
        }
