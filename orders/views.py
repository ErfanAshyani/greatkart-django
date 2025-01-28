import datetime

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from carts.models import Cart, CartItem
from orders.forms import OrderForm
from orders.models import Order, OrderProduct, Payment
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
from django.template.loader import render_to_string
import json

from store.models import Product
from django.core.mail import EmailMessage


ZP_API_REQUEST = f"https://sandbox.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = f"https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = f"https://sandbox.zarinpal.com/pg/StartPay/"

amount = 1000  # Rial / Required
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
phone = '09016707903'  # Optional
email = 'fanr052@gmail.com'
# Important: need to edit for realy server.
CallbackURL = 'http://127.0.0.1:8000/orders/verify/'
MERCHANT = "aa9f19e6-3863-4e57-be36-4dcb54dbd4a4"

#? sandbox merchant 
if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

# Create your views here.

def payments(request):
    return render(request,'orders/payments.html')





@login_required(login_url='login')
def place_order(request,total=0,quantity=0):
    current_user = request.user

    #if the cart count is equal to zere then redirect to shop
    cart_items  = CartItem.objects.filter(user=current_user,cart__status="open")
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect('store')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)

        grand_total =  0
        tax = 0
        for cart_item in cart_items:
           total +=(cart_item.product.price * cart_item.quantity)
           quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax    
        if form.is_valid():
            #store all the billing information inside order table
            try:
                order = Order.objects.get(user=request.user,is_ordered=False)
                order.first_name = form.cleaned_data['first_name']
                order.last_name = form.cleaned_data['last_name']
                order.phone = form.cleaned_data['phone']
                order.email = form.cleaned_data['email']
                order.address_line_1 = form.cleaned_data['address_line_1']
                order.address_line_2 = form.cleaned_data['address_line_2']
                order.country = form.cleaned_data['country']
                order.state = form.cleaned_data['state']
                order.city = form.cleaned_data['city']
                order.order_note = form.cleaned_data['order_note']
                order.ip = request.META.get('REMOTE_ADDR')
                order.save()

            except:
                    data = Order()
                    data.user = request.user
                    data.first_name = form.cleaned_data['first_name']
                    data.last_name = form.cleaned_data['last_name']
                    data.phone = form.cleaned_data['phone']
                    data.email = form.cleaned_data['email']
                    data.address_line_1 = form.cleaned_data['address_line_1']
                    data.address_line_2 = form.cleaned_data['address_line_2']
                    data.country = form.cleaned_data['country']
                    data.state = form.cleaned_data['state']
                    data.city = form.cleaned_data['city']
                    data.order_note = form.cleaned_data['order_note']
                    data.order_total = grand_total
                    data.tax = tax
                    data.ip = request.META.get('REMOTE_ADDR')
                    data.save()
                    # Generate order number 
                    yr = int(datetime.date.today().strftime('%Y'))
                    dt = int(datetime.date.today().strftime('%d'))
                    mt = int(datetime.date.today().strftime('%m'))
                    d = datetime.date(yr,mt,dt)
                    current_date = d.strftime("%Y%m%d") #20210312
                    order_number = current_date + str(data.id)
                    data.order_number = order_number
                    data.save()
           
                



      
            order = Order.objects.get(user=current_user,is_ordered=False)
            context ={
                'order' : order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }

            return render(request,'orders/payments.html',context)
    else:
        return redirect('checkout')


     
        




@login_required(login_url='login')
def send_request(request):
    cart_items  = CartItem.objects.filter(user=request.user)
    grand_total =  0
    total = 0
    tax = 0
    quantity = 0
    for cart_item in cart_items:
           total +=(cart_item.product.price * cart_item.quantity)
           quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = int(total + tax)  
   

    data = {
        "merchant_id": MERCHANT,
        "amount": grand_total,
        "description": description,
        "mobile": request.user.phone_number,
        "callback_url": CallbackURL,
        "email":request.user.email,
    }
    data = json.dumps(data)
    
    headers = {'content-type': 'application/json', 'content-length': str(len(data)) }
    try:
        response = requests.post(ZP_API_REQUEST, data=data,headers=headers, timeout=10)
        string = response.text
        b = json.loads(string)
        
        return ZP_API_STARTPAY + b["data"]["authority"]
    except requests.exceptions.Timeout:
        return {'status': False, 'code': 'timeout'}
    except requests.exceptions.ConnectionError:
        return {'status': False, 'code': 'connection error'}
    except Exception as e:
        return {'status': False, 'code2': 'connection error2'}

@login_required(login_url='login')
def verify(request):
    cart_items  = CartItem.objects.filter(user=request.user)
    grand_total =  0
    tax = 0
    total = 0
    quantity = 0
    for cart_item in cart_items:
           total +=(cart_item.product.price * cart_item.quantity)
           quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = int(total + tax) 
   
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    if status =='NOK':
        return redirect('checkout')
    data = {
        "merchant_id": MERCHANT,
        "amount": grand_total,
        "authority": authority,
    }
    data = json.dumps(data)
    # set content length by data
    headers = {'content-type': 'application/json', 'content-length': str(len(data)) }
    try:
      response = requests.post(ZP_API_VERIFY, data=data,headers=headers, timeout=10)
      string = response.text
      b = json.loads(string)
      if ((b["data"]["code"]==100) or (b["data"]["code"]==101)):
          #Store transaction details inside Payments
          payment = Payment(
              user = request.user,
              payment_id = b["data"]["ref_id"],
              payment_method = "ZarinPal",
              amount_paid = grand_total,
              status = "Completed",
          )
          payment.save()
          order = Order.objects.get(user=request.user,is_ordered=False)
          order.payment = payment
          order.is_ordered=True;
          order.save()

          #Move the cart items to order Product table
          cart_items = CartItem.objects.filter(user=request.user,cart__status="open")

          for item in cart_items:
              orderproduct = OrderProduct()
              orderproduct.order  = order
              orderproduct.payment = payment
              orderproduct.user  = request.user
              orderproduct.product = item.product 
              orderproduct.quantity = item.quantity
              orderproduct.product_price = item.product.price
              orderproduct.ordered = True
            #   orderproduct.variations = item.variations wrong for many to many fileld
              orderproduct.save()

              cart_item = CartItem.objects.get(id=item.id)
              product_variation = cart_item.variations.all()
              orderproduct = OrderProduct.objects.get(id=orderproduct.id)
              orderproduct.variations.set(product_variation)
              orderproduct.save()




          #reduce the quantity of the sold products
              product = Product.objects.get(id=item.product_id)
              product.stock -= item.quantity
              product.save()





          #closing cart of user
          cart_item = CartItem.objects.filter(user=request.user,cart__status="open").first()
          cart = cart_item.cart
          cart.status ="clos"
          cart.save()
          #send email to customer
          mail_subject = 'Thank you for your order!'
          message = render_to_string('orders/order_recieved_email.html',{
            'user' : request.user,
            'order': order,

            
            })
          to_email = request.user.email
          send_email = EmailMessage(mail_subject,message,to=[to_email])
          send_email.send() 
          print("here")

          #send order number and transaction id to thank you page
          data = {
              'order_number':order.order_number,
              'transID' : payment.payment_id
          }
          print("tehr")
          redirect_url = reverse('order_complete')
          redirect_url += f'?order_number={order.order_number}&payment_id={payment.payment_id}'
          return redirect(redirect_url)

        #   return render(request,'orders/order_complete.html',data)
      else:
        return redirect('checkout') 
    
       
 
    except Exception as e:
      print(e)
      return redirect('checkout')

@login_required(login_url='login')
def make_payment(request):
    print("1")
    if request.method == 'POST':
        print("2")
        # اطلاعات لازم را از درخواست دریافت کنید (مثلاً از فرم)
        response_request = send_request(request)

        
        
        return redirect(response_request)
    
def order_complete(request):
    order_number = request.GET.get('order_number')
    transId = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transId)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number' : order.order_number,
            'transID' : transId,
            'payment' : payment,
            'subtotal' : subtotal
    
        }
        return render(request,'orders/order_complete.html',context)
    except (Order.DoesNotExist,Payment.DoesNotExist):
        return redirect('home')
        
