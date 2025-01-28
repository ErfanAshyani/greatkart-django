from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from carts.models import Cart, CartItem
from orders.models import Order

from store.models import Product, Variation
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned

# Create your views here.

def cart(request,total=0,quantity=0,cart_items=None):
    tax = 0
    grand_total = 0
    try:

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True,cart__status="open")
        else:
                  
          cart = Cart.objects.get(cart_id=_cart_id(request),status="open")
          cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax    
    except Cart.DoesNotExist or CartItem.DoesNotExist:
        pass
    context ={
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total':grand_total,
    }         
    return render(request,'store/cart.html',context)

#adding undersore before name of function make it private
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart    

def add_cart(request,product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    user_open_carts = []
    cart = None
    if request.method =='POST':
       for item in request.POST:
           key = item
           value = request.POST[key]
        #    print(key,value)
           
           try:
               variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
               product_variation.append(variation)
           except:
               pass      

    #    color = request.POST['color']
       
    

    # return HttpResponse(color + size)


    
    try:
        if request.user.is_authenticated:
            order = Order.objects.filter(user=request.user,is_ordered=False)
            order.delete()
            #get all open carts of user
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)

            cart_items_check = CartItem.objects.get(user=request.user,is_active=True,cart__status="open")
            
            
            for item in cart_items:
                if item.cart in user_open_carts :
                    continue
                else:
                    if item.cart.status == 'open':
                     user_open_carts.append(item.cart)
            #get all products of all open carts of user    
        else:
            cart =Cart.objects.get(cart_id=_cart_id(request))
         #get the cart using th cart id returned in the session
    except (Cart.DoesNotExist,CartItem.DoesNotExist,ValueError):
        print("kkkk")
        # return HttpResponse(e)
        cart = Cart.objects.create(
            cart_id = _cart_id(request)        )  
        cart.save()
    except MultipleObjectsReturned:
        print("kk2kk")
        for item in cart_items:
                if item.cart in user_open_carts :
                    continue
                else:
                    if item.cart.status == 'open':
                     user_open_carts.append(item.cart)       
    
    if len(user_open_carts)==0:
        
        is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            # existing_variations -> database
            # current_variations -> product_variation
            #item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(ex_var_list) 
            if product_variation in ex_var_list:
                #increase cart quantity
                idex = ex_var_list.index(product_variation)
                item_id = id[idex]
                item = CartItem.objects.get(product=product,id=item_id)
                if request.user.is_authenticated:
                    item.user = request.user
                item.quantity +=1
                item.cart = cart
                item.save()
            else:
                item = CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
                
            
        else:
            if request.user.is_authenticated:
                cart_item = CartItem.objects.create(
                    product = product,
                    quantity =1,
                    user = request.user,
                    cart = cart
                )
            else:
                cart_item = CartItem.objects.create(
                    product = product,
                    quantity =1,
                    cart = cart
                )    
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save() 
    else:
       print(user_open_carts)
       for cart in user_open_carts:
        is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()      
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            # existing_variations -> database
            # current_variations -> product_variation
            #item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(ex_var_list) 
            if product_variation in ex_var_list:
                #increase cart quantity
                idex = ex_var_list.index(product_variation)
                item_id = id[idex]
                item.user =request.user
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity +=1
                item.save()
            else:
                item = CartItem.objects.create(product=product,user=request.user,quantity=1,cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
                
            
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity =1,
                user =request.user,
                cart = cart
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()    
    return redirect('cart')

def remove_cart(request,product_id,cart_item_id):    
    
    try: 
         if request.user.is_authenticated:
          product=get_object_or_404(Product,id=product_id)
          cart_item = CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
          order = Order.objects.filter(user=request.user,is_ordered=False)
          order.delete()
         else:   
          cart = Cart.objects.get(cart_id=_cart_id(request))
          product=get_object_or_404(Product,id=product_id)
          cart_item = CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
         if cart_item.quantity > 1:
                                   cart_item.quantity -= 1
                                   cart_item.save()
         else: 
            cart_item.delete()
    except:
         pass

    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    cart_item_1 = 1
    cart_item_2 = 2
    if request.user.is_authenticated:
        # cart = CartItem.objects.get(user=request.user,cart__status="open")
        # cart = cart.cart.cart_id
        order = Order.objects.filter(user=request.user,is_ordered=False)
        order.delete()
        product = get_object_or_404(Product,id=product_id)
        cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        cart = cart_item.cart
        cart_item.delete()
        try:
          cart_item_2 = CartItem.objects.get(user=request.user)
        except CartItem.DoesNotExist:
          cart_item_2 = None
        except MultipleObjectsReturned:
            pass 
         
        
    else:
        cart =Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product,id=product_id)
        cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        cart_item.delete()
        try:
          cart_item_1 = CartItem.objects.get(cart=cart)
        except CartItem.DoesNotExist:
          cart_item_1 = None
        except MultipleObjectsReturned:
            pass  

    
    
    

    

    if cart_item_1 is None or cart_item_2 is None:
        cart.delete()
    

    
    return redirect('cart')
@login_required(login_url='login')
def checkout(request,total=0,quantity=0,cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter()
            cart_items = CartItem.objects.filter(user=request.user,is_active=True,cart__status="open")
        else:
          cart = Cart.objects.get(cart_id=_cart_id(request))
          cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total +=(cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax    
    except Cart.DoesNotExist or CartItem.DoesNotExist:
        pass
    context ={
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total':grand_total,
        'user':request.user,
    }         
    return render(request,'store/checkout.html',context)                