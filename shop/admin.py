from django.contrib import admin
from .models import (
    Category, Product, ProductImage, ProductVariant, Brand, Tag, Review,
    Blog, Comment, SocialMedia, UserFollow, Program, ProgramCategory,
    ProgramEnrollment, Message, Booking, Session, Donation, Wishlist,
    Coupon, ShippingZone, ChatMessage
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 2


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'website']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_featured', 'sort_order']
    list_filter = ['is_featured', 'parent']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'sort_order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'original_price', 'stock', 'available',
                    'is_featured', 'is_bestseller', 'is_new_arrival']
    list_filter = ['available', 'created', 'updated', 'category', 'brand', 'is_featured',
                   'is_bestseller', 'is_new_arrival', 'condition']
    list_editable = ['price', 'available', 'is_featured', 'is_bestseller', 'stock']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description', 'sku']
    raw_id_fields = ['category', 'brand']
    filter_horizontal = ['tags']
    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'rating', 'verified_purchase', 'is_approved', 'created']
    list_filter = ['rating', 'verified_purchase', 'is_approved', 'created']
    list_editable = ['is_approved']
    search_fields = ['product__name', 'name', 'email']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'min_order_amount',
                    'max_uses', 'used_count', 'valid_from', 'valid_to', 'is_active']
    list_filter = ['discount_type', 'is_active']
    list_editable = ['is_active']
    search_fields = ['code']


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_rate', 'per_kg_rate', 'estimated_days']


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['blog', 'user', 'created']


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'icon_name', 'followers_count']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'created']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ProgramCategory)
class ProgramCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'mentor_name', 'time', 'capacity', 'meeting_type']
    list_filter = ['category', 'meeting_type']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['session_name', 'user', 'status', 'booked_at']
    list_filter = ['status']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'received_at']


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'amount', 'created_at']


@admin.register(ProgramEnrollment)
class ProgramEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'program', 'enrolled_at']
