from rest_framework import serializers
from shop.models import Category, Product, Blog, Comment, SocialMedia, ProgramCategory, Program, Message, Booking, ProgramEnrollment, Session, Donation
from orders.models import Order, OrderItem
from decimal import Decimal
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'slug', 'image', 'description', 'price', 'available', 'created']
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image: rep['image'] = instance.image.url
        return rep

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)
    cost = serializers.DecimalField(source='get_cost', max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity', 'cost']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(source='get_total_cost', max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'created', 'paid', 'items', 'total_cost']

class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']

class ProgramCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramCategory
        fields = ['id', 'name', 'slug']

class ProgramSerializer(serializers.ModelSerializer):
    category = ProgramCategorySerializer(read_only=True)
    class Meta:
        model = Program
        fields = ['id', 'category', 'title', 'slug', 'description', 'image', 'price', 'created']
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image: rep['image'] = instance.image.url
        return rep

class ProgramEnrollmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    program = ProgramSerializer(read_only=True)
    class Meta:
        model = ProgramEnrollment
        fields = ['id', 'user', 'program', 'enrolled_at']

class ShippingDetailsSerializer(serializers.Serializer):
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    email = serializers.EmailField()
    address = serializers.CharField()
    postalCode = serializers.CharField(source='postal_code')
    city = serializers.CharField()

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ['id', 'name', 'email', 'amount', 'message', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'blog', 'user', 'text', 'created']

class BlogSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'author', 'content', 'image', 'image_description', 'event_description', 'created', 'comments']

class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ['id', 'name', 'url', 'icon_name', 'followers_count']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'name', 'email', 'subject', 'body', 'received_at']

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'title', 'category', 'description', 'mentor_name', 'mentor_bio', 'time', 'duration', 'capacity', 'syllabus', 'prerequisites', 'image', 'meeting_type', 'meeting_link', 'created_at']

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    session = SessionSerializer(read_only=True)
    session_id = serializers.IntegerField(write_only=True, required=False)
    meeting_type = serializers.CharField(source='session.meeting_type', read_only=True)
    meeting_link = serializers.URLField(source='session.meeting_link', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'session', 'session_id', 'session_name', 'scheduled_time', 'notes', 'meeting_format', 'status', 'meeting_type', 'meeting_link', 'booked_at']
    
    def create(self, validated_data):
        session_id = validated_data.pop('session_id', None)
        if session_id:
            session = Session.objects.get(id=session_id)
            validated_data['session'] = session
            if not validated_data.get('session_name'):
                validated_data['session_name'] = session.title
        
        # If user is in context, assign it
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            
        return super().create(validated_data)

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

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    def create(self, val):
        return User.objects.create_user(**val)
