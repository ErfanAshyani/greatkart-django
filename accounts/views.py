from base64 import decodebytes, urlsafe_b64decode, urlsafe_b64encode
import base64
from multiprocessing import AuthenticationError

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

import accounts
from accounts.admin import AccountAdmin
from accounts.models import Account
from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order
from .forms import RegistrationForm
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site

#verification email 
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests

# Create your views here.

def register(request):
    if request.method == 'POST':
        obj =Account.objects.filter(email=request.POST["email"],is_active=False).first()
        if obj is not None:
          form = RegistrationForm(request.POST,instance=obj)
        else:
          form = RegistrationForm(request.POST)    
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            if obj is None:
               user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
               user.phone_number = phone_number
               user.save()
            else:
                user =  Account.objects.get(email=request.POST["email"])
                user.first_name = first_name
                user.last_name = last_name
                user.username = username
                user.password = password
                user.phone_number = phone_number
                user.save()



            #user_activation
            
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user' : user,
                'domain':current_site,
                'uid' :urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)

            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            form = RegistrationForm()
            messages.success(request,"Registeration email send.")
            return redirect('/accounts/login/?command=verification&email='+email)
            # در اینجا می‌توانید کارهای بیشتری انجام دهید مثل ریدایرکت به صفحه دیگر
        # اگر فرم نامعتبر باشد، به سادگی ادامه دهید و همان فرم را به قالب ارسال کنید
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        
            email = request.POST["email"]
            password = request.POST["password"]
            

            user = auth.authenticate(email=email,password=password)
            if user is not None:
                try:
                   
                   cart_itemold = CartItem.objects.filter(user=user,cart__status="open").first()

                   if cart_itemold is None:
                            cart = Cart.objects.get(cart_id=_cart_id(request))
                            is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                            if is_cart_item_exists:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()
                   else:
                       order = Order.objects.filter(user=request.user,is_ordered=False)
                       order.delete()
                       cartold = cart_itemold.cart
                       cart = Cart.objects.get(cart_id=_cart_id(request))
                       is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                       cart_itemold = CartItem.objects.filter(user=user,cart__status="open")
                       check_break = False
                       if is_cart_item_exists:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                
                                
                                        for itemold in cart_itemold:
                                         print(f"Item product: {item.product}, ItemOld product: {itemold.product}")
                                         print(f"Item variations: {item.variations}, ItemOld variations: {itemold.variations}")
                                         print(f"Type of Item variations: {type(item.variations)}, Type of ItemOld variations: {type(itemold.variations)}")
     


                                         check_break = False

                                         if (item.product == itemold.product) and (set(item.variations.all()) == set(itemold.variations.all())):
     

                                            print("hi i am here")
                                            itemold.quantity +=1
                                            itemold.save()
                                            item.delete()
                                            check_break = True
                                            break
                                        if check_break:
                                            continue
                                        print("hi i am here2") 
                                        item.user = user
                                        item.cart = cartold
                                        item.save()
                                cart.delete()   

                       
                                       
                except:
                    pass    
                auth.login(request,user)
                messages.success(request,'You are now login')
                
              
                if request.POST['next'] is None:
                      return redirect("dashboard")
                else:
                      return redirect(request.POST['next'])
                  
         
                
            else:
                messages.error(request,'Invalid login credentials!')
                # return redirect("home")


    # if a GET (or any other method) we'll create a blank form
    else:
        form = RegistrationForm()


    # context = {
    #     'form' : form,
    # }   

    return render(request,'accounts/login.html')
    
@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out')
    

    return redirect("login")


   

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Account  # فرض کنید مدل کاربر شما Account نام دارد

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request,"Invalid activation link")
        return redirect('register')
    

@login_required(login_url='login') 
def dashboard(request):
    return render(request,'accounts/dashboard.html')


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = 'Please reset your password'
            message = render_to_string('accounts/reset_password_email.html',{
                'user' : user,
                'domain':current_site,
                'uid' :urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)

            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Password reset email has been sent to your address')
            return redirect('login')
        else:
            messages.error(request,'Account with this email does not exist!')
            return redirect('forgotPassword')        
       

    return render(request,'accounts/forgotPassword.html')

def resetpassword_validate(request,uidb64,token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'Pleas reset your password')
        return redirect('resetPassword')


    else:
        messages.error(request,"This link has been expired!")
        return redirect('login')
def resetPassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password ==confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successful")
            return redirect("login")


        else:
            messages.error(request,"Password do not match")
            return redirect('resetPassword')
    else:
        return render(request,'accounts/resetPassword.html')   

    

     



   
