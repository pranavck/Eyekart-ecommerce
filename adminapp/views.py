from django.shortcuts import render , redirect
from store.models import Product
from accounts.models import Account
from carts.views import _cart_id
from carts.models import Cart,CartItem
from django.contrib import messages , auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.
def admin_login(request):
  if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email = email, password = password,is_admin=True)

        if user.is_superadmin:
          if user is not None:
              auth.login(request, user)
              request.session['key'] = "value"
                #messages.success(request, "You are Successfully Logged in")
              messages.success(request, 'Admin Logged in successfully')
              return redirect('admin_dashboard')
          else:
              messages.error(request, 'Admin Logged in failed')
              return redirect('admin_login')
  return render(request, 'admin/adminlogin.html')

def admin_dashboard(request):
  return render(request, 'admin/admindashboard.html')

def user_management(request): 
  users = Account.objects.all()
  context = {
    'users': users,
  }
  return render(request, 'admin/manage_user.html',context )

def delete_user(request,user_id):
    account = Account.objects.get(pk=user_id)
    account.delete()
    return redirect('manage_user')

def product_management(request):
  products = Product.objects.all()
  context = {
    'products': products,
  }
  return render(request, 'admin/product_management.html',context) 

def category_management(request):
  categories = Product.objects.all()
  context = {
    'categories': categories,
  }
  return render(request, 'admin/category_management.html',context) 

@login_required(login_url = 'admin_login')
def admin_logout(request):
  if request.session.has_key('key'):
    del(request.session['key'])
  messages.success(request , 'Logged Out Successfully')
  return redirect('admin_login')

def add_product(request):
  pass



