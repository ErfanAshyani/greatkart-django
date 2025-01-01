from django.shortcuts import get_object_or_404, render
from category.models import Category

from store.models import Product

# Create your views here.

def store(request,category_slug=None):
    categories = None;
    products = None;
    
    if category_slug != None:
        categories = get_object_or_404(Category,slug = category_slug)
        products = Product.objects.filter(category=categories,is_available=True)
        products_count = products.count()
    else:
       products = Product.objects.all().filter(is_available=True)      
    context = {
        'products' : products,
        'product_count': len(products)
    }
    return render(request,'store/store.html',context)

def product_detail(request,category_slug,product_slug):
    try:
        #syntaxt of get access to forenkey category__slug
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e:
        raise e
    context = {
      'single_product' : single_product  
    }    
    return render(request,'store/product-detail.html',context)
