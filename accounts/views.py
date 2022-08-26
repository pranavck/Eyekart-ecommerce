from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from email.policy import default
from django.shortcuts import redirect, render
from django.contrib import messages , auth
from store.models import Product
from accounts.models import Account, UserProfile
from django.contrib.auth.decorators import login_required

from orders.models import Order, OrderProduct
from .forms import RegistrationForm, UserProfileForm ,UserForm
from carts.views import _cart_id
from carts.models import Cart,CartItem

#email_verification


from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage

import requests

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)                       #taking for the form validation

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password)
            user.phone_number = phone_number
            user.save

            #user_activation

            current_site = get_current_site(request)
            mail_subject = 'Please Activate Your Account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message,to=[to_email])
            send_email.send()

            # messages.success(request, "Thank you for Registerng with Us, We have send u a verification email to your mail[pranavck04@gmail.com].Please Verify It.")
            return redirect('/accounts/login/?command=verification&email='+email)

        else:
            form = RegistrationForm()

    form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email = email, password = password)

        if user is not None:
            try:
                print('entering inside the try block')
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    print(cart_item)

                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                print('entering inside the except block')
                pass
            auth.login(request, user)
            #messages.success(request, "You are Successfully Logged in")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def signout(request):
    auth.logout(request)
    messages.success(request,"You are logged out")
    return redirect('login')

def activate(request ,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your Account is activated.")
        return redirect('login')
    else:
        messages.error(request, "Invalid Activation Link")
        return redirect('register')

@login_required(login_url= 'login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered =True)
    orders_count = orders.count
    context = {
        'orders_count' : orders_count
    }
    return render(request, 'accounts/dashboard.html', context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email = email).exists():
            user = Account.objects.get(email__exact=email)

            #reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your Password'
            message = render_to_string('accounts/reset_password_email.html',{
                'user' : user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message,to=[to_email])
            send_email.send()

            messages.success(request, "Password Reset email has been send to your Email Address.")
            return redirect('login')
        else:
            messages.error(request, "This Account doesn't exist")
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please Reset your Password")
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password Reset Successfull")
            return redirect('login')
        else:
            messages.error(request,"PassWords Don't Match")    
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')

@login_required(login_url='login')
def my_orders(request):
    orders = OrderProduct.objects.all().exclude(user = request.user, status="Cancelled").order_by('-created_at')
    context = {
        'orders' : orders,
    }
    return render(request, 'accounts/my_orders.html',context)

@login_required(login_url='login')
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form =UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your Profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    context = {
        'user_form' : user_form,
        'profile_form' : profile_form,
    }
    return render(request, 'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,"Password updated successfully")
                return redirect('change_password')
            else:
                messages.error(request, "Please enter valid Current password")
                return redirect('change_password')
        else:
            messages.error(request, "Passwords Does not match")
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number = order_id)
    order = Order.objects.get(order_number = order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail' : order_detail,
        'order' : order,
        'subtotal' : subtotal,
    }
    return render(request, 'accounts/order_detail.html',context)

def cancel_order(request,payment_id):
    order = OrderProduct.objects.get(user=request.user,payment=payment_id)
    item = Product.objects.get(user=request.user,pk=pk)
    item.stock += item.quantity
    item.save()
    order.status = "Cancelled"
    order.save()
    messages.success(request,"Order cancelled")
    return redirect('my_orders')