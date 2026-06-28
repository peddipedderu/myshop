from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import requests
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from decimal import Decimal
from shop.models import Category, Product, Blog, SocialMedia, ChatMessage, Program, ProgramCategory, Message, Booking, ProgramEnrollment, Comment, Session, Donation
from orders.models import Order, OrderItem
from cart.cart import Cart
from .serializers import (UserSerializer, 
    CategorySerializer, ProductSerializer, CartSerializer, OrderSerializer, 
    BlogSerializer, SocialMediaSerializer, OrderItemSerializer, 
    ProgramSerializer, ProgramCategorySerializer, MessageSerializer, 
    BookingSerializer, ProgramEnrollmentSerializer, CommentSerializer, 
    SessionSerializer, DonationSerializer
)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

class ProgramEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = ProgramEnrollment.objects.all()
    serializer_class = ProgramEnrollmentSerializer
    permission_classes = [IsAuthenticated]

class ProgramCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProgramCategory.objects.all()
    serializer_class = ProgramCategorySerializer
    permission_classes = [AllowAny]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

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

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [AllowAny]

class BlogViewSet(viewsets.ModelViewSet): 
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

class CommentViewSet(viewsets.ModelViewSet): 
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

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
        members_data = [
            {'id': 1, 'name': 'Sarah', 'role': 'Member', 'avatar': 'https://i.pravatar.cc/150?u=1'},
            {'id': 2, 'name': 'Elena', 'role': 'Follower', 'avatar': 'https://i.pravatar.cc/150?u=2'},
            {'id': 3, 'name': 'Amina', 'role': 'Member', 'avatar': 'https://i.pravatar.cc/150?u=3'},
            {'id': 4, 'name': 'Grace', 'role': 'Follower', 'avatar': 'https://i.pravatar.cc/150?u=4'},
            {'id': 5, 'name': 'Maya', 'role': 'Member', 'avatar': 'https://i.pravatar.cc/150?u=5'},
            {'id': 6, 'name': 'Zoe', 'role': 'Follower', 'avatar': 'https://i.pravatar.cc/150?u=6'},
            {'id': 7, 'name': 'Lila', 'role': 'Member', 'avatar': 'https://i.pravatar.cc/150?u=7'},
        ]
        return Response(members_data)

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

            return Response({
                'success': True, 
                'platform': platform.name, 
                'new_count': platform.followers_count
            })
        except SocialMedia.DoesNotExist:
            return Response({'error': 'Platform not found'}, status=404)

    @action(detail=False, methods=['get'], url_path='forums')
    def forums(self, request):
        categories = [
            {
                "id": 1,
                "title": "General Discussions",
                "description": "General discussions, community and space of sensations.",
                "threads_count": 45,
                "posts_count": 230,
                "icon_type": "general",
                "chat_room": "general"
            },
            {
                "id": 2,
                "title": "Wellness & Self-Care",
                "description": "Share tips and experiences on maintaining physical and mental well-being.",
                "threads_count": 32,
                "posts_count": 156,
                "icon_type": "wellness",
                "chat_room": "wellness"
            },
            {
                "id": 3,
                "title": "Books & Literature",
                "description": "Discuss your favorite books, authors, and literary works.",
                "threads_count": 28,
                "posts_count": 112,
                "icon_type": "book",
                "chat_room": "books"
            },
            {
                "id": 4,
                "title": "Events & Meetups",
                "description": "Find out about upcoming community events and coordinate meetups.",
                "threads_count": 15,
                "posts_count": 89,
                "icon_type": "events",
                "chat_room": "events"
            }
        ]
        trending = [
            {
                "id": 1,
                "title": "New Member Introductions",
                "last_post": "27 minutes ago",
                "posts_count": 12,
                "hot": True,
                "chat_room": "introductions"
            },
            {
                "id": 2,
                "title": "Share Your Story",
                "last_post": "23 minutes ago",
                "posts_count": 8,
                "hot": True,
                "chat_room": "stories"
            },
            {
                "id": 3,
                "title": "Upcoming Summer Workshop",
                "last_post": "45 minutes ago",
                "posts_count": 15,
                "hot": False,
                "chat_room": "workshop"
            },
            {
                "id": 4,
                "title": "Favorite Self-Care Routines",
                "last_post": "1 hour ago",
                "posts_count": 24,
                "hot": True,
                "chat_room": "routines"
            }
        ]
        return Response({
            'categories': categories,
            'trending': trending,
            'ws_base_url': 'ws://' + request.get_host() + '/ws/chat/'
        })

    @action(detail=False, methods=['get'], url_path='chat/history/(?P<room_name>[\w-]+)')
    def chat_history(self, request, room_name=None):
        messages = ChatMessage.objects.filter(room_name=room_name).order_by('timestamp')[:50]
        data = [
            {
                'username': m.username,
                'message': m.message,
                'timestamp': m.timestamp.isoformat()
            } for m in messages
        ]
        return Response(data)

class CommunityViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='forum/stats')
    def forum_stats(self, request):
        return Response({
            'active_threads': 124,
            'total_posts': 850,
            'members_online': 42
        })

class MessageViewSet(viewsets.ModelViewSet): 
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Send email notification to roy@pinkcycle.co.ke
        if response.status_code == 201:
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                name = request.data.get('name', 'Unknown')
                email = request.data.get('email', 'no-reply@pinkcycle.co.ke')
                subject = request.data.get('subject', 'No Subject')
                body = request.data.get('body', '')
                email_subject = f"[PinkCycle Contact] {subject} - from {name}"
                email_body = (
                    f"You have received a new message from the PinkCycle website.\n\n"
                    f"From: {name}\n"
                    f"Email: {email}\n"
                    f"Subject: {subject}\n\n"
                    f"Message:\n{body}\n\n"
                    f"---\n"
                    f"Reply directly to {email} to respond."
                )
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    ['roy@pinkcycle.co.ke'],
                    fail_silently=False,
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send contact email: {e}")
        return response

class SessionViewSet(viewsets.ModelViewSet): 
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        session = self.get_object()
        bookings_count = Booking.objects.filter(session=session).count()
        slots_remaining = session.capacity - bookings_count
        return Response({
            "capacity": session.capacity,
            "booked_count": bookings_count,
            "slots_remaining": slots_remaining,
            "fully_booked": slots_remaining <= 0
        })

    @action(detail=False, methods=['get'], url_path='Tech')
    def tech(self, request):
        queryset = self.queryset.filter(category__iexact='Tech')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='Career')
    def career(self, request):
        queryset = self.queryset.filter(category__iexact='Career')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='Wellness')
    def wellness(self, request):
        queryset = self.queryset.filter(category__iexact='Wellness')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='Finance')
    def finance(self, request):
        queryset = self.queryset.filter(category__iexact='Finance')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='Tech/Lifeskills')
    def lifeskills(self, request):
        queryset = self.queryset.filter(category__iexact='Life Skills')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet): 
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    @action(detail=True, methods=['get'])
    def join_meeting(self, request, pk=None):
        booking = self.get_object()
        if not booking.session or not booking.session.meeting_link:
            return Response({"detail": "No meeting link available for this session."}, status=404)
        
        # Log join activity or perform other backend logic here
        print(f"User {request.user} joined meeting for booking {booking.id}")
        
        return redirect(booking.session.meeting_link)

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
                "quantity": item.quantity,
                "price": str(item.price),
                "total": str(item.get_cost())
            })
        return Response({
            "order_id": order.id,
            "items": items,
            "total_amount": str(order.get_total_cost()),
            "first_name": order.first_name,
            "last_name": order.last_name,
            "email": order.email
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
            callback_url = callback_url.replace('http://localhost', 'https://resolution-beta-lightbox-ala.trycloudflare.com')
            callback_url = callback_url.replace('http://127.0.0.1:8000', 'https://resolution-beta-lightbox-ala.trycloudflare.com')

        with open("/tmp/mpesa_callback.log", "a") as f:
            f.write(f"Initiating STK push: Phone={formatted_phone}, Amount={amount}, Order={order.id}, Callback={callback_url}\n")

        try:
            response = cl.stk_push(
                phone_number=formatted_phone,
                amount=amount,
                account_reference=f"chk_{order.id}",
                transaction_desc=f"Pay Order {order.id}",
                callback_url=callback_url
            )
            if getattr(response, 'response_code', None) == '0':
                checkout_id = getattr(response, 'checkout_request_id', '')
                order.mpesa_checkout_id = checkout_id
                order.save()
                with open("/tmp/mpesa_callback.log", "a") as f:
                    f.write(f"STK push success for order {order.id}: checkout_id={checkout_id}\n")
                return Response({
                    "detail": "STK Push initiated successfully.",
                    "checkout_request_id": checkout_id
                }, status=status.HTTP_200_OK)
            else:
                error_msg = getattr(response, 'response_description', 'STK Push initiation failed.')
                error_code = getattr(response, 'response_code', 'Unknown')
                with open("/tmp/mpesa_callback.log", "a") as f:
                    f.write(f"STK push failed: code={error_code}, desc={error_msg}\n")
                return Response({
                    "detail": error_msg,
                    "response_code": error_code
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            with open("/tmp/mpesa_callback.log", "a") as f:
                f.write(f"Error in STK push: {str(e)}\n{tb}\n")
            return Response({"detail": f"Error initiating payment: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='callback')
    def mpesa_callback(self, request):
        import logging
        logger = logging.getLogger(__name__)
        data = request.data
        logger.info(f"Mpesa callback data: {data}")
        with open("/tmp/mpesa_callback.log", "a") as f:
            f.write(f"CALLBACK RECEIVED: {data}\n")

        body = data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        result_code = stk_callback.get('ResultCode')
        checkout_request_id = stk_callback.get('CheckoutRequestID')

        if checkout_request_id:
            from orders.models import Order
            try:
                order = Order.objects.get(mpesa_checkout_id=checkout_request_id)
                if result_code == 0:
                    order.paid = True
                    metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                    receipt_number = None
                    for item in metadata:
                        if item.get('Name') == 'MpesaReceiptNumber':
                            receipt_number = item.get('Value')
                            break
                    if receipt_number:
                        order.mpesa_receipt_number = receipt_number
                    order.save()
                    with open("/tmp/mpesa_callback.log", "a") as f:
                        f.write(f"ORDER {order.id} PAID SUCCESSFULLY, RECEIPT: {receipt_number}\n")
                else:
                    with open("/tmp/mpesa_callback.log", "a") as f:
                        f.write(f"ORDER {order.id} PAYMENT FAILED OR CANCELLED, RESULT CODE: {result_code}\n")
            except Order.DoesNotExist:
                with open("/tmp/mpesa_callback.log", "a") as f:
                    f.write(f"ORDER NOT FOUND FOR CHECKOUT ID: {checkout_request_id}\n")

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

        from orders.models import Order
        order = get_object_or_404(Order, id=order_id)
        return Response({
            "order_id": order.id,
            "paid": order.paid,
            "mpesa_receipt": order.mpesa_receipt_number,
            "paypal_order_id": order.paypal_order_id
        })

    @action(detail=False, methods=['delete'], url_path='cancel')
    def cancel_order(self, request):
        order_id = request.data.get('order_id') or request.query_params.get('order_id') or request.session.get('order_id')
        if not order_id:
            return Response({"detail": "Order ID not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        if isinstance(order_id, str):
            order_id = order_id.replace('chk_', '')
            
        from orders.models import Order
        try:
            order = Order.objects.get(id=order_id)
            order.delete()
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
            
        if 'order_id' in request.session:
            del request.session['order_id']
            request.session.modified = True
            
        return Response({"detail": "Order cancelled and deleted successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='process')
    def process_payment(self, request):
        order_id = request.session.get('order_id')
        if not order_id:
            return Response({"detail": "No order found in session. Please add items to cart and checkout first."}, status=status.HTTP_400_BAD_REQUEST)
        
        return redirect('payment:process')

    @action(detail=False, methods=['post'], url_path='paypal/create')
    def create_paypal_order(self, request):
        import requests
        from django.conf import settings
        from orders.models import Order

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

        # Get access token from PayPal
        try:
            token_response = requests.post(
                f"{api_url}/v1/oauth2/token",
                auth=(client_id, secret_key),
                data={"grant_type": "client_credentials"},
                timeout=15
            )
            if token_response.status_code != 200:
                return Response({
                    "detail": "Failed to authenticate with PayPal.",
                    "paypal_error": token_response.json()
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            token_data = token_response.json()
            access_token = token_data.get('access_token')
        except Exception as e:
            return Response({"detail": f"Error authenticating with PayPal: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create Order on PayPal
        total_amount = str(order.get_total_cost())
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Build URLs
        return_url = "https://pinkcycle.co.ke/payment_successfully?gateway=paypal"
        cancel_url = "https://pinkcycle.co.ke/payment_canceled?gateway=paypal"
        
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": f"chk_{order.id}",
                    "amount": {
                        "currency_code": "USD",
                        "value": total_amount
                    },
                    "description": f"Order #{order.id} on PinkCycle"
                }
            ],
            "application_context": {
                "brand_name": "PinkCycle",
                "landing_page": "NO_PREFERENCE",
                "user_action": "PAY_NOW",
                "return_url": return_url,
                "cancel_url": cancel_url
            }
        }

        try:
            order_response = requests.post(
                f"{api_url}/v2/checkout/orders",
                headers=headers,
                json=payload,
                timeout=15
            )
            if order_response.status_code not in [200, 201]:
                return Response({
                    "detail": "Failed to create PayPal order.",
                    "paypal_error": order_response.json()
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            paypal_data = order_response.json()
            paypal_order_id = paypal_data.get('id')
            
            order.paypal_order_id = paypal_order_id
            order.save()
            
            # Find the approval link
            approve_url = None
            for link in paypal_data.get('links', []):
                if link.get('rel') == 'approve':
                    approve_url = link.get('href')
                    break
            
            if not approve_url:
                return Response({"detail": "Approval link not found in PayPal response."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            return Response({
                "approval_url": approve_url,
                "paypal_order_id": paypal_order_id,
                "order_id": order.id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"detail": f"Error creating PayPal order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=['post'], url_path='paypal/capture')
    def capture_paypal_order(self, request):
        import requests
        from django.conf import settings
        from orders.models import Order

        paypal_order_id = request.data.get('paypal_order_id')
        order_id = request.data.get('order_id')
        
        if not paypal_order_id:
            return Response({"detail": "PayPal Order ID (paypal_order_id) is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve local order
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
                return Response({"detail": f"No order found matching PayPal Order ID {paypal_order_id}."}, status=status.HTTP_404_NOT_FOUND)

        if order.paid:
            return Response({
                "success": True,
                "detail": "Order has already been marked as paid.",
                "order_id": order.id,
                "customer_email": order.email,
                "amount_total": int(order.get_total_cost() * 100),
                "currency": "usd",
                "payment_intent": order.paypal_capture_id or order.paypal_order_id or paypal_order_id
            }, status=status.HTTP_200_OK)

        client_id = settings.PAYPAL_CLIENT_ID
        secret_key = settings.PAYPAL_SECRET_KEY
        api_url = settings.PAYPAL_API_URL

        # Get access token from PayPal
        try:
            token_response = requests.post(
                f"{api_url}/v1/oauth2/token",
                auth=(client_id, secret_key),
                data={"grant_type": "client_credentials"},
                timeout=15
            )
            if token_response.status_code != 200:
                return Response({
                    "detail": "Failed to authenticate with PayPal.",
                    "paypal_error": token_response.json()
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            token_data = token_response.json()
            access_token = token_data.get('access_token')
        except Exception as e:
            return Response({"detail": f"Error authenticating with PayPal: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Capture payment
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        try:
            capture_response = requests.post(
                f"{api_url}/v2/checkout/orders/{paypal_order_id}/capture",
                headers=headers,
                json={},
                timeout=15
            )
            
            capture_data = capture_response.json()
            
            if capture_response.status_code not in [200, 201]:
                # Check if it was already captured
                if capture_data.get('details', [{}])[0].get('issue') == 'ORDER_ALREADY_CAPTURED':
                    order.paid = True
                    order.save()
                    return Response({
                        "success": True,
                        "detail": "Payment was already captured on PayPal.",
                        "order_id": order.id,
                        "customer_email": order.email,
                        "amount_total": int(order.get_total_cost() * 100),
                        "currency": "usd",
                        "payment_intent": order.paypal_capture_id or order.paypal_order_id or paypal_order_id
                    }, status=status.HTTP_200_OK)
                    
                return Response({
                    "detail": "Failed to capture PayPal order.",
                    "paypal_error": capture_data
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Check status of payment
            status_paypal = capture_data.get('status')
            if status_paypal == 'COMPLETED':
                order.paid = True
                # Extract capture ID
                capture_id = None
                try:
                    payments = capture_data.get('purchase_units', [{}])[0].get('payments', {})
                    captures = payments.get('captures', [{}])
                    capture_id = captures[0].get('id')
                    order.paypal_capture_id = capture_id
                except (IndexError, KeyError):
                    pass
                order.save()
                
                return Response({
                    "success": True,
                    "detail": "Payment captured successfully.",
                    "order_id": order.id,
                    "paypal_status": status_paypal,
                    "customer_email": order.email,
                    "amount_total": int(order.get_total_cost() * 100),
                    "currency": "usd",
                    "payment_intent": capture_id or paypal_order_id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "detail": f"PayPal transaction status is {status_paypal}",
                    "order_id": order.id,
                    "paypal_status": status_paypal
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({"detail": f"Error capturing PayPal order: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckoutViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    @action(detail=False, methods=['post'])
    def shipping(self, request):
        from .serializers import ShippingDetailsSerializer
        serializer = ShippingDetailsSerializer(data=request.data)
        if serializer.is_valid():
            cart = Cart(request)
            if not cart: return Response({"success": False, "message": "Cart is empty."}, status=400)
            order = Order.objects.create(**serializer.validated_data)
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            # Store order_id in session for payment process
            request.session['order_id'] = order.id
            total_amount = order.get_total_cost()
            cart.clear()
            return Response({
                "success": True, 
                "data": {
                    "checkoutId": f"chk_{order.id}",
                    "total_amount": str(total_amount)
                }
            }, status=201)
        return Response({"success": False, "errors": serializer.errors}, status=400)

from rest_framework.views import APIView
 
 
from .serializers import UserRegistrationSerializer, UserSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User registered."}, status=201)
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
        
        # Add additional components for the account page
        data['orders_count'] = Order.objects.filter(email=user.email).count()
        data['bookings_count'] = Booking.objects.filter(user=user).count() if 'user' in [f.name for f in Booking._meta.get_fields()] else 0
        data['enrollments_count'] = ProgramEnrollment.objects.filter(user=user).count()
        
        return Response(data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
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
                
                with open("/tmp/google_auth.log", "a") as f:
                    f.write(f"DEBUG: Exchange attempt with curl - code={code[:10]}... redirect_uri={redirect_uri}\n")
                
                # Using curl as a workaround for Python 3.13 SSL EOF issues
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
                    try:
                        token_data = json.loads(result.stdout)
                        if "access_token" in token_data:
                            access_token = token_data.get("access_token")
                        else:
                            with open("/tmp/google_auth.log", "a") as f:
                                f.write(f"DEBUG: Exchange failed (API) - {result.stdout}\n")
                            return Response({"detail": "Failed to exchange code", "error": token_data}, status=400)
                    except Exception as e:
                        return Response({"detail": "Failed to parse Google response", "error": str(e)}, status=400)
                else:
                    with open("/tmp/google_auth.log", "a") as f:
                        f.write(f"DEBUG: Exchange failed (CURL) - {result.stderr}\n")
                    return Response({"detail": "Failed to reach Google via curl"}, status=400)

            if not access_token:
                return Response({'detail': 'Access token is required'}, status=400)
                
            # Use curl for userinfo as well
            curl_userinfo = ["curl", "-s", f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={access_token}"]
            result_ui = subprocess.run(curl_userinfo, capture_output=True, text=True)
            
            if result_ui.returncode != 0:
                return Response({'detail': 'Failed to reach Google userinfo via curl'}, status=400)
                
            data = json.loads(result_ui.stdout)
            email = data.get('email')
            first_name = data.get('given_name', data.get('first_name', ''))
            last_name = data.get('family_name', data.get('last_name', ''))
            
            if not email:
                return Response({'detail': 'Email not provided by Google', 'debug': result_ui.stdout}, status=400)
                
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
            
            token, _ = Token.objects.get_or_create(user=user)
            with open("/tmp/google_auth.log", "a") as f:
                f.write(f"DEBUG: Login success for {email}\n")
            return Response({'token': token.key, 'user': UserSerializer(user).data})
        except Exception as e:
            with open("/tmp/google_auth.log", "a") as f:
                f.write(f"DEBUG: CRASH in google_login: {str(e)}\n{traceback.format_exc()}\n")
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
                with open("/tmp/password_reset.log", "a") as f:
                    f.write(f"EMAIL: {email} | LINK: {reset_url}\n")
            except Exception:
                pass
            
            subject = f"Password Reset Request for {email}"
            message = (
                f"CLIENT_EMAIL: {email}\n"
                f"RESET_LINK: {reset_url}\n\n"
                f"Hello {user.username},\n\n"
                f"You requested a password reset for your PinkCycle account.\n"
                f"Please click the link below to reset your password:\n\n"
                f"{reset_url}\n\n"
                f"If you did not request this, please ignore this email.\n\n"
                f"Best regards,\nPinkCycle Team"
            )
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@pinkcycle.co.ke',
                    ['roy@pinkcycle.co.ke'],
                    fail_silently=False,
                )
            except Exception as e:
                # Log email failure but still return reset_url for local/dev use
                try:
                    with open("/tmp/password_reset.log", "a") as f:
                        f.write(f"EMAIL_ERROR: {str(e)}\n")
                except Exception:
                    pass
            
            return Response({
                "detail": "If the email is registered, a password reset link has been sent."
            }, status=200)
        
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
        return Response({"detail": "Password has been reset successfully."}, status=200)
