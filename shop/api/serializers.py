from rest_framework import serializers
from shop.models import (
    Category, Product, Blog, Comment, SocialMedia, ProgramCategory, Program,
    Message, Booking, ProgramEnrollment, Session, Donation, Brand, Tag,
    ProductImage, ProductVariant, Review, Wishlist, Coupon, ShippingZone
)
from orders.models import Order, OrderItem
from decimal import Decimal
from django.contrib.auth.models import User


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'description', 'website']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'parent', 'is_featured', 'sort_order', 'subcategories']

    def get_subcategories(self, obj):
        return CategorySerializer(obj.subcategories.all(), many=True).data

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url
        return rep


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'sort_order']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url
        return rep


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'value', 'price_modifier', 'stock', 'sku']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'name', 'email', 'rating', 'title', 'body', 'verified_purchase',
                  'helpful_votes', 'created', 'is_approved']
        read_only_fields = ['verified_purchase', 'helpful_votes', 'is_approved']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    discount_percentage = serializers.IntegerProperty = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'category_slug', 'brand_name',
            'name', 'slug', 'image', 'short_description', 'price', 'original_price',
            'available', 'stock', 'in_stock', 'is_featured', 'is_bestseller', 'is_new_arrival',
            'discount_percentage', 'average_rating', 'review_count', 'created'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url
        rep['discount_percentage'] = instance.discount_percentage
        rep['average_rating'] = instance.average_rating
        rep['review_count'] = instance.review_count
        rep['in_stock'] = instance.in_stock
        return rep


class ProductSerializer(serializers.ModelSerializer):
    """Full serializer for product detail."""
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'brand', 'tags', 'name', 'slug', 'image', 'images',
            'description', 'short_description', 'price', 'original_price',
            'available', 'stock', 'in_stock', 'condition', 'sku', 'weight', 'dimensions',
            'is_featured', 'is_bestseller', 'is_new_arrival', 'views_count',
            'discount_percentage', 'average_rating', 'review_count',
            'variants', 'reviews', 'created', 'updated'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url
        rep['discount_percentage'] = instance.discount_percentage
        rep['average_rating'] = instance.average_rating
        rep['review_count'] = instance.review_count
        rep['in_stock'] = instance.in_stock
        return rep


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_image = serializers.SerializerMethodField()
    cost = serializers.DecimalField(source='get_cost', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'product_image', 'price', 'quantity', 'cost']

    def get_product_image(self, obj):
        if obj.product.image:
            return obj.product.image.url
        return None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(source='get_total_cost', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'first_name', 'last_name', 'email', 'address', 'postal_code',
            'city', 'phone', 'notes', 'status', 'payment_method',
            'created', 'updated', 'paid', 'items', 'total_cost',
            'mpesa_checkout_id', 'mpesa_receipt_number',
            'paypal_order_id', 'paypal_capture_id', 'stripe_payment_intent'
        ]


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
        if instance.image:
            rep['image'] = instance.image.url
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
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField()
    postalCode = serializers.CharField(source='postal_code')
    city = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField(required=False, allow_blank=True)


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
        fields = [
            'id', 'title', 'category', 'description', 'mentor_name', 'mentor_bio',
            'time', 'duration', 'capacity', 'syllabus', 'prerequisites',
            'image', 'meeting_type', 'meeting_link', 'created_at'
        ]


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    session = SessionSerializer(read_only=True)
    session_id = serializers.IntegerField(write_only=True, required=False)
    meeting_type = serializers.CharField(source='session.meeting_type', read_only=True)
    meeting_link = serializers.URLField(source='session.meeting_link', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'session', 'session_id', 'session_name',
            'scheduled_time', 'notes', 'meeting_format', 'status',
            'meeting_type', 'meeting_link', 'booked_at'
        ]

    def create(self, validated_data):
        session_id = validated_data.pop('session_id', None)
        if session_id:
            session = Session.objects.get(id=session_id)
            validated_data['session'] = session
            if not validated_data.get('session_name'):
                validated_data['session_name'] = session.title
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
                'image': item['product'].image.url if item['product'].image else None,
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
            'total_items': len(items),
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, val):
        return User.objects.create_user(**val)


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'added_at']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_type', 'discount_value', 'min_order_amount',
                  'max_uses', 'used_count', 'valid_from', 'valid_to', 'is_active', 'description']


class ShippingZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingZone
        fields = ['id', 'name', 'regions', 'base_rate', 'per_kg_rate', 'estimated_days']
