from rest_framework import serializers
from shop.models import Category, Product
from decimal import Decimal
from cart.cart import Cart
from orders.models import Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'name', 'slug', 'image', 'description', 'price',
            'available', 'created', 'updated'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            representation['image'] = instance.image.url
        return representation


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Calculate total price for this cart item
        representation['total_price'] = Decimal(instance['price']) * instance['quantity']
        return representation


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def to_representation(self, instance):
        items = [
            {
                'product_id': item['product'].id,
                'name': item['product'].name,
                'quantity': item['quantity'],
                'price': item['price'],
                'total_price': Decimal(item['price']) * item['quantity'],
            }
            for item in instance
        ]
        total_price = instance.get_total_price()
        return {
            'items': items,
            'total_price': total_price,
        }


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product'
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'price', 'quantity', 'get_cost']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'address',
            'postal_code',
            'city',
            'created',
            'updated',
            'paid',
            'items',
            'total_cost',
        ]

    def get_total_cost(self, obj):
        return obj.get_total_cost()

