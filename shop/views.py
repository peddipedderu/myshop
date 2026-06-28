from django.shortcuts import get_object_or_404, render
from .models import Category, Product


def product_list(request, category_slug=None):
    category = None
    if category_slug:
        special_filters = ['deals', 'featured', 'new-arrivals', 'bestsellers']
        if category_slug in special_filters:
            class VirtualCategory:
                def __init__(self, name, slug):
                    self.name = name
                    self.slug = slug
                    self.parent = None
            category = VirtualCategory(category_slug.replace('-', ' ').title(), category_slug)
        else:
            category = get_object_or_404(Category, slug=category_slug)
    return render(request, 'shop/product/list.html', {'category': category})


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'shop/product/detail.html', {'product': product})


def checkout_view(request):
    return render(request, 'shop/checkout.html')


def account_view(request):
    return render(request, 'shop/account.html')


def reset_password_view(request):
    return render(request, 'shop/reset_password.html')


def search_view(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    return render(request, 'shop/search.html', {'query': query, 'category': category})
