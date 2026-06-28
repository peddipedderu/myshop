from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import requests
from django.contrib.auth.models import User
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, Avg, Count, F
from decimal import Decimal
from django.utils import timezone
from shop.models import (
    Category, Product, Blog, SocialMedia, ChatMessage, Program, ProgramCategory,
    Message, Booking, ProgramEnrollment, Comment, Session, Donation,
    Brand, Tag, ProductImage, ProductVariant, Review, Wishlist, Coupon, ShippingZone
)
from orders.models import Order, OrderItem
from cart.cart import Cart
from .serializers import (
    UserSerializer, CategorySerializer, ProductSerializer, ProductListSerializer,
    CartSerializer, OrderSerializer, BlogSerializer, SocialMediaSerializer,
    OrderItemSerializer, ProgramSerializer, ProgramCategorySerializer, MessageSerializer,
    BookingSerializer, ProgramEnrollmentSerializer, CommentSerializer, SessionSerializer,
    DonationSerializer, BrandSerializer, TagSerializer, ReviewSerializer,
    WishlistSerializer, CouponSerializer, ShippingZoneSerializer,
    ShippingDetailsSerializer, UserRegistrationSerializer
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ─────────────────────────── BRAND ────────────────────────────────────────────
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


# ─────────────────────────── TAG ──────────────────────────────────────────────
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


# ─────────────────────────── SHIPPING ZONE ────────────────────────────────────
class ShippingZoneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ShippingZone.objects.all()
    serializer_class = ShippingZoneSerializer
    permission_classes = [AllowAny]


# ─────────────────────────── COUPON ───────────────────────────────────────────
class CouponViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='validate')
    def validate_coupon(self, request):
        code = request.data.get('code', '').strip().upper()
        order_amount = Decimal(str(request.data.get('order_amount', 0)))
        if not code:
            return Response({'valid': False, 'message': 'Coupon code is required.'}, status=400)
        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True)
        except Coupon.DoesNotExist:
            return Response({'valid': False, 'message': 'Invalid coupon code.'}, status=404)
        now = timezone.now()
        if coupon.valid_from > now:
            return Response({'valid': False, 'message': 'This coupon is not yet active.'}, status=400)
        if coupon.valid_to < now:
            return Response({'valid': False, 'message': 'This coupon has expired.'}, status=400)
        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            return Response({'valid': False, 'message': 'This coupon has reached its usage limit.'}, status=400)
        if order_amount < coupon.min_order_amount:
            return Response({
                'valid': False,
                'message': f'Minimum order amount is KES {coupon.min_order_amount} to use this coupon.'
            }, status=400)
        if coupon.discount_type == 'percentage':
            discount = (order_amount * coupon.discount_value) / 100
        else:
            discount = min(coupon.discount_value, order_amount)
        return Response({
            'valid': True,
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': str(coupon.discount_value),
            'discount_amount': str(discount),
            'description': coupon.description
        })


# ─────────────────────────── CATEGORY ─────────────────────────────────────────
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('featured'):
            qs = qs.filter(is_featured=True)
        if self.request.query_params.get('top_level'):
            qs = qs.filter(parent=None)
        return qs

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        category = get_object_or_404(Category, slug=slug)
        # Include subcategory products
        category_ids = [category.id] + list(category.subcategories.values_list('id', flat=True))
        products = Product.objects.filter(category__in=category_ids, available=True)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(products, request)
        serializer = ProductListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


# ─────────────────────────── PRODUCT ──────────────────────────────────────────
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(available=True).select_related('category', 'brand').prefetch_related('tags', 'images', 'variants', 'reviews')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name', 'brand__name', 'tags__name']
    ordering_fields = ['price', 'created', 'name', 'views_count']
    ordering = ['-created']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        category = params.get('category')
        brand = params.get('brand')
        tag = params.get('tag')
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        featured = params.get('featured')
        bestseller = params.get('bestseller')
        new_arrival = params.get('new_arrival')
        condition = params.get('condition')
        in_stock = params.get('in_stock')
        deals = params.get('deals')

        if category:
            cat = Category.objects.filter(slug=category).first()
            if cat:
                cat_ids = [cat.id] + list(cat.subcategories.values_list('id', flat=True))
                qs = qs.filter(category__in=cat_ids)
            else:
                qs = qs.filter(category__slug=category)

        if brand:
            qs = qs.filter(brand__slug=brand)
        if tag:
            qs = qs.filter(tags__slug=tag)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if featured:
            qs = qs.filter(is_featured=True)
        if bestseller:
            qs = qs.filter(is_bestseller=True)
        if new_arrival:
            qs = qs.filter(is_new_arrival=True)
        if condition:
            qs = qs.filter(condition=condition)
        if in_stock:
            qs = qs.filter(stock__gt=0)
        if deals:
            qs = qs.filter(original_price__isnull=False, original_price__gt=F('price'))

        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views
        Product.objects.filter(pk=instance.pk).update(views_count=instance.views_count + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        product = self.get_object()
        related = Product.objects.filter(
            category=product.category, available=True
        ).exclude(id=product.id)[:8]
        serializer = ProductListSerializer(related, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        products = self.get_queryset().filter(is_featured=True)[:12]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def bestsellers(self, request):
        products = self.get_queryset().filter(is_bestseller=True)[:12]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        products = self.get_queryset().filter(is_new_arrival=True)[:12]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def deals(self, request):
        """Products with discounts (original_price > price)."""
        products = self.get_queryset().filter(
            original_price__isnull=False
        ).extra(where=["original_price > price"])[:12]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'results': [], 'count': 0})
        products = self.get_queryset().filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()[:20]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response({'results': serializer.data, 'count': products.count()})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Shop statistics for dashboard."""
        return Response({
            'total_products': Product.objects.filter(available=True).count(),
            'total_categories': Category.objects.count(),
            'total_brands': Brand.objects.count(),
            'featured_count': Product.objects.filter(is_featured=True).count(),
            'bestseller_count': Product.objects.filter(is_bestseller=True).count(),
        })


# ─────────────────────────── REVIEW ───────────────────────────────────────────
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.filter(is_approved=True)
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        product = get_object_or_404(Product, id=product_id)
        # Check if user has purchased - set verified_purchase
        verified = False
        if self.request.user.is_authenticated:
            verified = OrderItem.objects.filter(
                order__email=self.request.user.email,
                order__paid=True,
                product=product
            ).exists()
        if self.request.user.is_authenticated:
            serializer.save(
                product=product,
                user=self.request.user,
                name=self.request.user.get_full_name() or self.request.user.username,
                email=self.request.user.email,
                verified_purchase=verified
            )
        else:
            serializer.save(product=product, verified_purchase=False)

    @action(detail=True, methods=['post'])
    def helpful(self, request, pk=None):
        review = self.get_object()
        review.helpful_votes += 1
        review.save()
        return Response({'helpful_votes': review.helpful_votes})


# ─────────────────────────── WISHLIST ─────────────────────────────────────────
class WishlistViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        items = Wishlist.objects.filter(user=request.user).select_related('product')
        serializer = WishlistSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        return Response({
            'added': created,
            'message': 'Added to wishlist' if created else 'Already in wishlist'
        }, status=201 if created else 200)

    @action(detail=False, methods=['delete'])
    def remove(self, request):
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.filter(user=request.user, product=product).delete()
        return Response({'message': 'Removed from wishlist'})

    @action(detail=False, methods=['get'])
    def check(self, request):
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'in_wishlist': False})
        in_wishlist = Wishlist.objects.filter(user=request.user, product_id=product_id).exists()
        return Response({'in_wishlist': in_wishlist})


# ─────────────────────────── CART ─────────────────────────────────────────────
class CartViewSet(viewsets.ViewSet):
    def list(self, request):
        cart = Cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        override = request.data.get('override', False)
        product = get_object_or_404(Product, id=product_id)
        if not product.in_stock:
            return Response({'detail': 'Product is out of stock.'}, status=400)
        cart = Cart(request)
        cart.add(product, quantity, override_quantity=override)
        updated_cart = CartSerializer(cart).data
        return Response({
            "detail": "Product added to cart.",
            "cart": updated_cart
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        cart.remove(product)
        return Response({"detail": "Product removed from cart.", "cart": CartSerializer(cart).data})

    @action(detail=False, methods=['put'])
    def update_quantity(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({"detail": "Quantity is required."}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        cart.add(product, int(quantity), override_quantity=True)
        return Response({"detail": "Product quantity updated.", "cart": CartSerializer(cart).data})

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        cart = Cart(request)
        cart.clear()
        return Response({"detail": "Cart cleared."})

    @action(detail=False, methods=['get'])
    def count(self, request):
        cart = Cart(request)
        return Response({'count': len(cart), 'total': str(cart.get_total_price())})


# ─────────────────────────── ORDER ────────────────────────────────────────────
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(email=self.request.user.email)
        return qs

    @action(detail=True, methods=['get'])
    def track(self, request, pk=None):
        order = self.get_object()
        return Response({
            'order_id': order.id,
            'status': order.status,
            'tracking_number': order.tracking_number,
            'paid': order.paid,
            'payment_method': order.payment_method,
            'created': order.created,
            'items_count': order.items.count(),
            'total': str(order.get_total_cost()),
        })


# ─────────────────────────── PAYMENT ──────────────────────────────────────────
class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        order_items = OrderItem.objects.all()
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        order_id = request.session.get('order_id')
        if not order_id:
            return Response({"detail": "No order found in session."}, status=status.HTTP_404_NOT_FOUND)
        order = get_object_or_404(Order, id=order_id)
        items = []
        for item in order.items.all():
            items.append({
                "name": item.product.name,
                "image": item.product.image.url if item.product.image else None,
                "quantity": item.quantity,
                "price": str(item.price),
                "total": str(item.get_cost())
            })
        return Response({
            "order_id": order.id,
            "items": items,
            "subtotal": str(order.get_subtotal()),
            "discount_amount": str(order.discount_amount),
            "shipping_amount": str(order.shipping_amount),
            "total_amount": str(order.get_total_cost()),
            "first_name": order.first_name,
            "last_name": order.last_name,
            "email": order.email,
            "phone": order.phone,
            "address": order.address,
            "city": order.city,
        })

    @action(detail=False, methods=['post'])
    def lipa_na_mpesa(self, request):
        from django_daraja.mpesa.core import MpesaClient
        from django_daraja.mpesa.utils import format_phone_number
        from orders.models import Order

        phone_number = request.data.get('phone_number')
        amount_val = request.data.get('amount')
        order_id = request.data.get('order_id')

        if not phone_number:
            return Response({"detail": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not order_id:
            return Response({"detail": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(order_id, str):
            order_id = order_id.replace('chk_', '')

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        if not amount_val:
            amount_val = order.get_total_cost()

        try:
            amount = int(float(amount_val))
        except (ValueError, TypeError):
            return Response({"detail": "Invalid amount value."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"detail": "Amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            formatted_phone = format_phone_number(phone_number)
        except Exception:
            formatted_phone = phone_number

        cl = MpesaClient()
        callback_url = request.build_absolute_uri('/api/payment/callback/')
        if 'localhost' in callback_url or '127.0.0.1' in callback_url:
            callback_url = callback_url.replace('http://localhost', 'https://pinkcycle.co.ke')
            callback_url = callback_url.replace('http://127.0.0.1:8000', 'https://pinkcycle.co.ke')

        try:
            response = cl.stk_push(
                phone_number=formatted_phone,
                amount=amount,
                account_reference=f"chk_{order.id}",
                transaction_desc=f"PinkCycle Order {order.id}",
                callback_url=callback_url
            )
            if getattr(response, 'response_code', None) == '0':
                checkout_id = getattr(response, 'checkout_request_id', '')
                order.mpesa_checkout_id = checkout_id
                order.payment_method = 'mpesa'
                order.save()
                return Response({
                    "detail": "STK Push initiated. Please check your phone and enter your M-Pesa PIN.",
                    "checkout_request_id": checkout_id
                }, status=status.HTTP_200_OK)
            else:
                error_msg = getattr(response, 'response_description', 'STK Push initiation failed.')
                return Response({"detail": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Error initiating payment: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='callback')
    def mpesa_callback(self, request):
        import logging
        logger = logging.getLogger(__name__)
        data = request.data
        body = data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        result_code = stk_callback.get('ResultCode')
        checkout_request_id = stk_callback.get('CheckoutRequestID')

        if checkout_request_id:
            try:
                order = Order.objects.get(mpesa_checkout_id=checkout_request_id)
                if result_code == 0:
                    order.paid = True
                    order.status = 'confirmed'
                    metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                    for item in metadata:
                        if item.get('Name') == 'MpesaReceiptNumber':
                            order.mpesa_receipt_number = item.get('Value')
                            break
                    order.save()
            except Order.DoesNotExist:
                logger.warning(f"Order not found for checkout ID: {checkout_request_id}")
        return Response({"ResultCode": 0, "ResultDesc": "Success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='status')
    def check_status(self, request):
        order_id = request.query_params.get('order_id')
        if not order_id:
            order_id = request.session.get('order_id')
        if not order_id:
            return Response({"detail": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(order_id, str):
            order_id = order_id.replace('chk_', '')
        order = get_object_or_404(Order, id=order_id)
        return Response({
            "order_id": order.id,
            "paid": order.paid,
            "status": order.status,
            "mpesa_receipt": order.mpesa_receipt_number,
            "paypal_order_id": order.paypal_order_id,
            "stripe_payment_intent": order.stripe_payment_intent
        })

    @action(detail=False, methods=['delete'], url_path='cancel')
    def cancel_order(self, request):
        order_id = request.data.get('order_id') or request.query_params.get('order_id') or request.session.get('order_id')
        if not order_id:
            return Response({"detail": "Order ID not found."}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(order_id, str):
            order_id = order_id.replace('chk_', '')
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'cancelled'
            order.save()
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        if 'order_id' in request.session:
            del request.session['order_id']
            request.session.modified = True
        return Response({"detail": "Order cancelled."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='paypal/create')
    def create_paypal_order(self, request):
        from django.conf import settings
        order_id = request.data.get('order_id') or request.session.get('order_id')
        if not order_id:
            return Response({"detail": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(order_id, str):
            order_id = order_id.replace('chk_', '')
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        if order.paid:
            return Response({"detail": "Order has already been paid."}, status=status.HTTP_400_BAD_REQUEST)

        client_id = settings.PAYPAL_CLIENT_ID
        secret_key = settings.PAYPAL_SECRET_KEY
        api_url = settings.PAYPAL_API_URL

        try:
            token_response = requests.post(
                f"{api_url}/v1/oauth2/token",
                auth=(client_id, secret_key),
                data={"grant_type": "client_credentials"},
                timeout=15
            )
            if token_response.status_code != 200:
                return Response({"detail": "Failed to authenticate with PayPal."}, status=500)
            access_token = token_response.json().get('access_token')
        except Exception as e:
            return Response({"detail": f"PayPal auth error: {str(e)}"}, status=500)

        total_amount = str(order.get_total_cost())
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        return_url = "https://pinkcycle.co.ke/payment_successfully?gateway=paypal"
        cancel_url = "https://pinkcycle.co.ke/payment_canceled?gateway=paypal"

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "reference_id": f"chk_{order.id}",
                "amount": {"currency_code": "USD", "value": total_amount},
                "description": f"PinkCycle Order #{order.id}"
            }],
            "application_context": {
                "brand_name": "PinkCycle Shop",
                "user_action": "PAY_NOW",
                "return_url": return_url,
                "cancel_url": cancel_url
            }
        }

        try:
            order_response = requests.post(f"{api_url}/v2/checkout/orders", headers=headers, json=payload, timeout=15)
            if order_response.status_code not in [200, 201]:
                return Response({"detail": "Failed to create PayPal order.", "error": order_response.json()}, status=500)
            paypal_data = order_response.json()
            paypal_order_id = paypal_data.get('id')
            order.paypal_order_id = paypal_order_id
            order.payment_method = 'paypal'
            order.save()
            approve_url = next((l['href'] for l in paypal_data.get('links', []) if l.get('rel') == 'approve'), None)
            if not approve_url:
                return Response({"detail": "PayPal approval link not found."}, status=500)
            return Response({
                "approval_url": approve_url,
                "paypal_order_id": paypal_order_id,
                "order_id": order.id
            })
        except Exception as e:
            return Response({"detail": f"PayPal error: {str(e)}"}, status=500)

    @action(detail=False, methods=['post'], url_path='paypal/capture')
    def capture_paypal_order(self, request):
        from django.conf import settings
        paypal_order_id = request.data.get('paypal_order_id')
        order_id = request.data.get('order_id')
        if not paypal_order_id:
            return Response({"detail": "PayPal Order ID is required."}, status=400)
        order = None
        if order_id:
            if isinstance(order_id, str):
                order_id = order_id.replace('chk_', '')
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                pass
        if not order:
            try:
                order = Order.objects.get(paypal_order_id=paypal_order_id)
            except Order.DoesNotExist:
                return Response({"detail": "Order not found."}, status=404)
        if order.paid:
            return Response({"success": True, "detail": "Already paid.", "order_id": order.id})

        client_id = settings.PAYPAL_CLIENT_ID
        secret_key = settings.PAYPAL_SECRET_KEY
        api_url = settings.PAYPAL_API_URL

        try:
            token_response = requests.post(
                f"{api_url}/v1/oauth2/token",
                auth=(client_id, secret_key),
                data={"grant_type": "client_credentials"},
                timeout=15
            )
            access_token = token_response.json().get('access_token')
        except Exception as e:
            return Response({"detail": f"PayPal auth error: {str(e)}"}, status=500)

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        try:
            capture_response = requests.post(
                f"{api_url}/v2/checkout/orders/{paypal_order_id}/capture",
                headers=headers, json={}, timeout=15
            )
            capture_data = capture_response.json()
            if capture_data.get('status') == 'COMPLETED':
                order.paid = True
                order.status = 'confirmed'
                try:
                    capture_id = capture_data['purchase_units'][0]['payments']['captures'][0]['id']
                    order.paypal_capture_id = capture_id
                except (KeyError, IndexError):
                    pass
                order.save()
                return Response({"success": True, "detail": "Payment captured.", "order_id": order.id})
            return Response({"success": False, "detail": f"Status: {capture_data.get('status')}"}, status=400)
        except Exception as e:
            return Response({"detail": f"Capture error: {str(e)}"}, status=500)

    @action(detail=False, methods=['post'], url_path='stripe/create')
    def create_stripe_payment(self, request):
        import stripe
        from django.conf import settings
        stripe.api_key = settings.STRIPE_SECRET_KEY
        order_id = request.data.get('order_id') or request.session.get('order_id')
        if not order_id:
            return Response({"detail": "Order ID is required."}, status=400)
        if isinstance(order_id, str):
            order_id = order_id.replace('chk_', '')
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=404)

        try:
            # Amount in cents (KES)
            amount = int(order.get_total_cost() * 100)
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='kes',
                metadata={'order_id': order.id},
                automatic_payment_methods={'enabled': True},
            )
            order.stripe_payment_intent = intent.id
            order.payment_method = 'stripe'
            order.save()
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'order_id': order.id,
                'amount': amount,
            })
        except stripe.error.StripeError as e:
            return Response({"detail": str(e)}, status=400)


# ─────────────────────────── CHECKOUT ─────────────────────────────────────────
class CheckoutViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def shipping(self, request):
        serializer = ShippingDetailsSerializer(data=request.data)
        if serializer.is_valid():
            cart = Cart(request)
            if not cart:
                return Response({"success": False, "message": "Cart is empty."}, status=400)

            data = serializer.validated_data
            # Handle coupon
            coupon_code = request.data.get('coupon_code', '')
            discount_amount = Decimal('0')
            shipping_amount = Decimal('0')

            cart_total = cart.get_total_price()

            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
                    now = timezone.now()
                    if coupon.valid_from <= now <= coupon.valid_to:
                        if coupon.discount_type == 'percentage':
                            discount_amount = (cart_total * coupon.discount_value) / 100
                        else:
                            discount_amount = min(coupon.discount_value, cart_total)
                        coupon.used_count += 1
                        coupon.save()
                except Coupon.DoesNotExist:
                    pass

            # Estimate shipping
            city = data.get('city', '')
            if city.lower() in ['nairobi', 'nairobi city']:
                shipping_amount = Decimal('200')
            elif city.lower() in ['mombasa', 'kisumu', 'nakuru', 'eldoret']:
                shipping_amount = Decimal('350')
            else:
                shipping_amount = Decimal('500')

            order = Order.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data.get('phone', ''),
                address=data['address'],
                postal_code=data['postal_code'],
                city=data['city'],
                notes=data.get('notes', ''),
                payment_method=data.get('payment_method', ''),
                coupon_code=coupon_code if discount_amount > 0 else '',
                discount_amount=discount_amount,
                shipping_amount=shipping_amount,
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )

            request.session['order_id'] = order.id
            cart.clear()

            return Response({
                "success": True,
                "data": {
                    "checkoutId": f"chk_{order.id}",
                    "order_id": order.id,
                    "subtotal": str(cart_total),
                    "discount_amount": str(discount_amount),
                    "shipping_amount": str(shipping_amount),
                    "total_amount": str(order.get_total_cost()),
                    "first_name": order.first_name,
                    "email": order.email,
                }
            }, status=201)
        return Response({"success": False, "errors": serializer.errors}, status=400)

    @action(detail=False, methods=['get'])
    def shipping_rates(self, request):
        """Return shipping rates for different cities."""
        return Response({
            'rates': [
                {'zone': 'Nairobi', 'cities': ['Nairobi', 'Nairobi City'], 'rate': '200', 'days': '1-2'},
                {'zone': 'Major Towns', 'cities': ['Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Thika'], 'rate': '350', 'days': '2-3'},
                {'zone': 'Rest of Kenya', 'cities': ['Other locations'], 'rate': '500', 'days': '3-5'},
            ]
        })


# ─────────────────────────── DONATION ─────────────────────────────────────────
class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [AllowAny]


# ─────────────────────────── BLOG ─────────────────────────────────────────────
class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# ─────────────────────────── SOCIAL MEDIA ─────────────────────────────────────
class SocialMediaViewSet(viewsets.ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer

    @action(detail=False, methods=['get'])
    def meta(self, request):
        socials = self.get_queryset()
        total_followers = sum(s.followers_count for s in socials)
        user_follows = []
        if request.user.is_authenticated:
            from shop.models import UserFollow
            user_follows = list(UserFollow.objects.filter(user=request.user).values_list('social_media_id', flat=True))
        return Response({
            'title': 'Join Our Community',
            'subtitle': 'Connect with us on social media and be part of the change.',
            'total_followers': total_followers,
            'user_follows': user_follows,
            'platforms': self.get_serializer(socials, many=True).data
        })

    @action(detail=False, methods=['get'])
    def members(self, request):
        return Response([
            {'id': i, 'name': n, 'role': r, 'avatar': f'https://i.pravatar.cc/150?u={i}'}
            for i, (n, r) in enumerate([
                ('Sarah', 'Member'), ('Elena', 'Follower'), ('Amina', 'Member'),
                ('Grace', 'Follower'), ('Maya', 'Member'), ('Zoe', 'Follower'), ('Lila', 'Member')
            ], 1)
        ])

    @action(detail=False, methods=['post'])
    def follow(self, request):
        platform_name = request.data.get('platform')
        if not platform_name:
            return Response({'error': 'Platform is required'}, status=400)
        try:
            platform = SocialMedia.objects.get(name__iexact=platform_name)
            platform.followers_count += 1
            platform.save()
            if request.user.is_authenticated:
                from shop.models import UserFollow
                UserFollow.objects.get_or_create(user=request.user, social_media=platform)
            return Response({'success': True, 'platform': platform.name, 'new_count': platform.followers_count})
        except SocialMedia.DoesNotExist:
            return Response({'error': 'Platform not found'}, status=404)

    @action(detail=False, methods=['get'], url_path='forums')
    def forums(self, request):
        categories = [
            {"id": 1, "title": "General Discussions", "description": "General discussions.", "threads_count": 45, "posts_count": 230, "icon_type": "general", "chat_room": "general"},
            {"id": 2, "title": "Wellness & Self-Care", "description": "Health and wellness tips.", "threads_count": 32, "posts_count": 156, "icon_type": "wellness", "chat_room": "wellness"},
            {"id": 3, "title": "Books & Literature", "description": "Book clubs and reviews.", "threads_count": 28, "posts_count": 112, "icon_type": "book", "chat_room": "books"},
            {"id": 4, "title": "Events & Meetups", "description": "Community events.", "threads_count": 15, "posts_count": 89, "icon_type": "events", "chat_room": "events"},
            {"id": 5, "title": "Shop Reviews", "description": "Share your shopping experience.", "threads_count": 20, "posts_count": 145, "icon_type": "shop", "chat_room": "shop"},
        ]
        trending = [
            {"id": 1, "title": "New Member Introductions", "last_post": "27 minutes ago", "posts_count": 12, "hot": True, "chat_room": "introductions"},
            {"id": 2, "title": "Best Deals This Week", "last_post": "5 minutes ago", "posts_count": 8, "hot": True, "chat_room": "deals"},
            {"id": 3, "title": "Upcoming Workshop", "last_post": "45 minutes ago", "posts_count": 15, "hot": False, "chat_room": "workshop"},
            {"id": 4, "title": "Product Reviews", "last_post": "1 hour ago", "posts_count": 24, "hot": True, "chat_room": "reviews"},
        ]
        return Response({
            'categories': categories,
            'trending': trending,
            'ws_base_url': 'ws://' + request.get_host() + '/ws/chat/'
        })

    @action(detail=False, methods=['get'], url_path='chat/history/(?P<room_name>[\\w-]+)')
    def chat_history(self, request, room_name=None):
        messages = ChatMessage.objects.filter(room_name=room_name).order_by('timestamp')[:50]
        return Response([
            {'username': m.username, 'message': m.message, 'timestamp': m.timestamp.isoformat()}
            for m in messages
        ])


# ─────────────────────────── COMMUNITY ────────────────────────────────────────
class CommunityViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='forum/stats')
    def forum_stats(self, request):
        return Response({'active_threads': 124, 'total_posts': 850, 'members_online': 42})


# ─────────────────────────── PROGRAM ──────────────────────────────────────────
class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs


class ProgramEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = ProgramEnrollment.objects.all()
    serializer_class = ProgramEnrollmentSerializer
    permission_classes = [IsAuthenticated]


class ProgramCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProgramCategory.objects.all()
    serializer_class = ProgramCategorySerializer
    permission_classes = [AllowAny]


# ─────────────────────────── MESSAGE ──────────────────────────────────────────
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                name = request.data.get('name', 'Unknown')
                email = request.data.get('email', 'no-reply@pinkcycle.co.ke')
                subject = request.data.get('subject', 'No Subject')
                body = request.data.get('body', '')
                send_mail(
                    f"[PinkCycle Contact] {subject} - from {name}",
                    f"From: {name}\nEmail: {email}\n\nMessage:\n{body}",
                    settings.DEFAULT_FROM_EMAIL,
                    ['roy@pinkcycle.co.ke'],
                    fail_silently=True,
                )
            except Exception:
                pass
        return response


# ─────────────────────────── SESSION / BOOKING ────────────────────────────────
class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        session = self.get_object()
        booked = Booking.objects.filter(session=session).count()
        remaining = session.capacity - booked
        return Response({
            "capacity": session.capacity,
            "booked_count": booked,
            "slots_remaining": remaining,
            "fully_booked": remaining <= 0
        })

    @action(detail=False, methods=['get'], url_path='Tech')
    def tech(self, request):
        return Response(self.get_serializer(self.queryset.filter(category__iexact='Tech'), many=True).data)

    @action(detail=False, methods=['get'], url_path='Career')
    def career(self, request):
        return Response(self.get_serializer(self.queryset.filter(category__iexact='Career'), many=True).data)

    @action(detail=False, methods=['get'], url_path='Wellness')
    def wellness(self, request):
        return Response(self.get_serializer(self.queryset.filter(category__iexact='Wellness'), many=True).data)

    @action(detail=False, methods=['get'], url_path='Finance')
    def finance(self, request):
        return Response(self.get_serializer(self.queryset.filter(category__iexact='Finance'), many=True).data)

    @action(detail=False, methods=['get'], url_path='Tech/Lifeskills')
    def lifeskills(self, request):
        return Response(self.get_serializer(self.queryset.filter(category__iexact='Life Skills'), many=True).data)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


# ─────────────────────────── AUTH ─────────────────────────────────────────────
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "detail": "User registered successfully.",
                "token": token.key,
                "user": UserSerializer(user).data
            }, status=201)
        return Response(serializer.errors, status=400)


class UserAccountViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['google_login', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        user = request.user
        serializer = UserSerializer(user)
        data = serializer.data
        data['orders_count'] = Order.objects.filter(email=user.email).count()
        data['bookings_count'] = Booking.objects.filter(user=user).count()
        data['enrollments_count'] = ProgramEnrollment.objects.filter(user=user).count()
        data['wishlist_count'] = Wishlist.objects.filter(user=user).count()
        data['reviews_count'] = Review.objects.filter(user=user).count()
        return Response(data)

    @action(detail=False, methods=['get'])
    def orders(self, request):
        orders = Order.objects.filter(email=request.user.email).order_by('-created')[:20]
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=401)
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()
        return Response(UserSerializer(user).data)

    @action(detail=False, methods=['post'])
    def google_login(self, request):
        import subprocess
        import json
        import traceback
        try:
            access_token = request.data.get('access_token')
            code = request.data.get('code')
            if code:
                from django.conf import settings
                client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
                client_secret = getattr(settings, "GOOGLE_CLIENT_SECRET", "")
                redirect_uri = request.data.get("redirect_uri")
                curl_cmd = [
                    "curl", "-s", "-X", "POST", "https://oauth2.googleapis.com/token",
                    "-d", f"code={code}",
                    "-d", f"client_id={client_id}",
                    "-d", f"client_secret={client_secret}",
                    "-d", f"redirect_uri={redirect_uri}",
                    "-d", "grant_type=authorization_code"
                ]
                result = subprocess.run(curl_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    token_data = json.loads(result.stdout)
                    if "access_token" in token_data:
                        access_token = token_data.get("access_token")
                    else:
                        return Response({"detail": "Failed to exchange code", "error": token_data}, status=400)
                else:
                    return Response({"detail": "Failed to reach Google"}, status=400)
            if not access_token:
                return Response({'detail': 'Access token is required'}, status=400)
            curl_userinfo = ["curl", "-s", f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={access_token}"]
            result_ui = subprocess.run(curl_userinfo, capture_output=True, text=True)
            if result_ui.returncode != 0:
                return Response({'detail': 'Failed to get user info from Google'}, status=400)
            data = json.loads(result_ui.stdout)
            email = data.get('email')
            if not email:
                return Response({'detail': 'Email not provided by Google'}, status=400)
            first_name = data.get('given_name', '')
            last_name = data.get('family_name', '')
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': UserSerializer(user).data})
        except Exception as e:
            return Response({"detail": f"Internal server error: {str(e)}"}, status=500)

    @action(detail=False, methods=['post'])
    def login(self, request):
        u, p = request.data.get('username'), request.data.get('password')
        if u and '@' in u:
            try:
                user_obj = User.objects.filter(email__iexact=u).first()
                if user_obj:
                    u = user_obj.username
            except Exception:
                pass
        user = authenticate(username=u, password=p)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': UserSerializer(user).data})
        return Response({'detail': 'Invalid credentials'}, status=400)


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required."}, status=400)
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"https://pinkcycle.co.ke/reset_password?uid={uid}&token={token}"
            try:
                send_mail(
                    "Password Reset Request",
                    f"CLIENT_EMAIL: {user.email}\nRESET_LINK: {reset_url}",
                    'noreply@pinkcycle.co.ke',
                    ['roy@pinkcycle.co.ke'],
                    fail_silently=True,
                )
            except Exception:
                pass
        return Response({"detail": "If the email is registered, a password reset link has been sent."}, status=200)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        if not all([uidb64, token, password, confirm_password]):
            return Response({"detail": "All fields are required."}, status=400)
        if password != confirm_password:
            return Response({"detail": "Passwords do not match."}, status=400)
        if len(password) < 6:
            return Response({"detail": "Password must be at least 6 characters."}, status=400)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid reset link."}, status=400)
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired reset token."}, status=400)
        user.set_password(password)
        user.save()
        return Response({"detail": "Password reset successfully."}, status=200)
