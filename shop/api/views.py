from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from decimal import Decimal
from shop.models import Category, Product
from orders.models import Order, OrderItem
from cart.cart import Cart
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
)
from .tasks import order_created
from django.conf import settings
import stripe
from django.urls import reverse
import requests
from django_daraja.mpesa.core import MpesaClient

# Stripe API configuration
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        quantity = int(request.data.get('quantity', 1))
        cart = Cart(request)
        cart.add(product, quantity)
        request.session.modified = True
        
        order_data = [{
            "product_name": product.name,
            "cost": product.price * quantity
        }]

        return Response({"detail": "Product added to cart.", "order_data": order_data}, status=status.HTTP_201_CREATED)

class CartViewSet(viewsets.ViewSet):
    def list(self, request):
        cart = Cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        cart.add(product, quantity)
        return Response({"detail": "Product added to cart."}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        cart.remove(product)
        return Response({"detail": "Product removed from cart."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put'])
    def update_quantity(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({"detail": "Quantity is required."}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        cart.add(product, quantity, override_quantity=True)
        return Response({"detail": "Product quantity updated."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        cart = Cart(request)
        cart.clear()
        return Response({"detail": "Cart cleared."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart = Cart(request)
        total_cost = Decimal('0.00')
        items = []

        for item in cart:
            product_id = item['product'].id
            product_name = item['product'].name
            product_price = item['price']
            quantity = item['quantity']
            item_total = product_price * quantity

            items.append({
                "id": product_id,
                "name": product_name,
                "quantity": quantity,
                "price": str(product_price),
                "total": str(item_total)
            })

            total_cost += item_total

        if total_cost <= 0:
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "items": items,
            "total_price": str(total_cost)
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def send_order(self, request):
        cart = Cart(request)
        order_items = []

        for item in cart:
            order_items.append({
                "product_id": item['product'].id,
                "price": item['price'],
                "quantity": item['quantity'],
            })

        if not order_items:
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        order_data = {"items": order_items}
        serializer = OrderSerializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=get_object_or_404(Product, id=item['product_id']),
                price=item['price'],
                quantity=item['quantity'],
            )

        payment_data = {
            "products": [
                {
                    "name": item['product_id'],  
                    "price": item['price'],
                    "quantity": item['quantity'],
                } for item in order_items
            ]
        }

        payment_response = requests.post(
            request.build_absolute_uri(reverse('payment:process')),
            json=payment_data
        )

        if payment_response.status_code != 200:
            return Response({"detail": "Payment processing failed."}, status=status.HTTP_400_BAD_REQUEST)

        cart.clear()
        order_created.delay(order.id)
        return Response({"detail": "Order created successfully.", "order_id": order.id}, status=status.HTTP_201_CREATED)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        cart = Cart(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity'],
            )
        cart.clear()
        order_created.delay(order.id)
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        order = get_object_or_404(Order, pk=pk)
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        cart = Cart(request)
        order_data = []
        
        for item in cart:
            order_data.append({
                "product_name": item['product'].name,
                "cost": item['price'] * item['quantity'],
            })

        return Response(order_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        Order.objects.all().delete()
        return Response({"detail": "All orders cleared."}, status=status.HTTP_204_NO_CONTENT)

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def list(self, request):
        order_items = self.get_queryset()
        serializer = self.get_serializer(order_items, many=True)

        total_price = Decimal('0.00')
        for item in order_items:
            total_price += item.price * item.quantity

        response_data = {
            "order_items": serializer.data,
            "total_price": str(total_price)
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def lipa_na_mpesa(self, request):
        cl = MpesaClient()
        phone_number = '0743192968'
        amount = 1
        account_reference = 'reference'
        transaction_desc = 'Description'
        callback_url = 'https://darajambili.herokuapp.com/express-payment'
        
        response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
        return Response(response)

    def stk_push_callback(self, request):
        data = request.body
        return Response("STK Push in Django")

    def payment_process(self, request):
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)

        if request.method == 'POST':
            success_url = request.build_absolute_uri(reverse('payment:completed'))
            cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

            session_data = {
                'phone_number': '0743192968',
                'amount': 1,
                'account_reference': 'reference',
                'transaction_desc': 'Description',
                'callback_url': 'https://darajambili.herokuapp.com/express-payment'
            }

            session = cl.stk_push(**session_data)
            return redirect(session.url, code=303)

        return render(request, 'payment/process.html')

    def payment_completed(self, request):
        return render(request, 'payment/completed.html')

    def payment_canceled(self, request):
        return render(request, 'payment/canceled.html')
        
        
    @action(detail=False, methods=['post'], url_path='process')
    def process_payment(self, request):
        # Directly reference products from the existing order items
        order_items = self.get_queryset()  # Assuming this retrieves the relevant order items
        products = []

        for item in order_items:
            products.append({
                "name": item.product.name,
                "price": item.price,  # Assuming price is in the correct format
                "quantity": item.quantity,
            })

        # Prepare Stripe checkout session data
        success_url = request.build_absolute_uri(reverse('payment:completed'))  # Update as needed
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))   # Update as needed

        session_data = {
            'mode': 'payment',
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [],
        }

        # Add products to the Stripe checkout session
        for product in products:
            try:
                price = int(product['price'] * Decimal('100'))  # Convert to cents
                quantity = int(product['quantity'])
            except (ValueError, TypeError):
                return Response({"detail": "Price and quantity must be valid numbers."}, status=status.HTTP_400_BAD_REQUEST)

            session_data['line_items'].append(
                {
                    'price_data': {
                        'unit_amount': price,  # Amount in cents
                        'currency': 'usd',
                        'product_data': {
                            'name': product['name'],
                        },
                    },
                    'quantity': quantity,
                }
            )

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(**session_data)
        self.clear_order_items()
        # Redirect to Stripe payment form
        return redirect(session.url, code=303)

    def clear_order_items(self):
        """ Clear all order items from the database. """
        self.queryset.delete()
