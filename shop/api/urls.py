from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (RegisterView, 
    CategoryViewSet, ProductViewSet, CartViewSet, OrderViewSet,
    BlogViewSet, SocialMediaViewSet, ProgramViewSet, ProgramCategoryViewSet,
    MessageViewSet, BookingViewSet, ProgramEnrollmentViewSet,
    CommentViewSet, SessionViewSet, DonationViewSet, PaymentViewSet, CheckoutViewSet, RegisterView, UserAccountViewSet, CommunityViewSet,
    PasswordResetView, PasswordResetConfirmView
)

app_name = 'shop'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'blog', BlogViewSet, basename='blog')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'join-us', SocialMediaViewSet, basename='join-us')
router.register(r'community', CommunityViewSet, basename='community')
router.register(r'programs', ProgramViewSet, basename='programs')
router.register(r'program-categories', ProgramCategoryViewSet, basename='program-category')
router.register(r'message', MessageViewSet, basename='message')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'sessions', SessionViewSet, basename='sessions')
router.register(r'enrollments', ProgramEnrollmentViewSet, basename='enrollment')
router.register(r'donations', DonationViewSet, basename='donations')
router.register(r'payment', PaymentViewSet, basename='payment')
router.register(r'checkout', CheckoutViewSet, basename='checkout')
router.register(r'account', UserAccountViewSet, basename='account')

urlpatterns = [
    path('api/bookings/Tech/', SessionViewSet.as_view({'get': 'tech'}), name='api-bookings-tech'),
    path('api/bookings/Career/', SessionViewSet.as_view({'get': 'career'}), name='api-bookings-career'),
    path('api/bookings/Wellness/', SessionViewSet.as_view({'get': 'wellness'}), name='api-bookings-wellness'),
    path('api/bookings/Finance/', SessionViewSet.as_view({'get': 'finance'}), name='api-bookings-finance'),
    path('api/bookings/Tech/Lifeskills/', SessionViewSet.as_view({'get': 'lifeskills'}), name='api-bookings-lifeskills'),
    path('api/login/', UserAccountViewSet.as_view({'post': 'login'}), name='api-login'),
    path('api/register/', RegisterView.as_view(), name='api-register'),
    path('api/password_reset/', PasswordResetView.as_view(), name='api-password-reset'),
    path('api/password_reset_confirm/', PasswordResetConfirmView.as_view(), name='api-password-reset-confirm'),
    path('api/', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
]
