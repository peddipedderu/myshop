from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('shop/', views.product_list, name='shop_home'),
    path('shop/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('shop/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout', views.checkout_view, name='checkout_no_slash'),
    path('account/', views.account_view, name='account'),
    path('account', views.account_view, name='account_no_slash'),
    path('search/', views.search_view, name='search'),
    path('search', views.search_view, name='search_no_slash'),
    path('reset_password/', views.reset_password_view, name='reset_password'),
    path('reset_password', views.reset_password_view, name='reset_password_no_slash'),
]
