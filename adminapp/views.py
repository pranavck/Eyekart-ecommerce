from django.http import HttpResponse
from urllib import request, response
from django.shortcuts import render , redirect
from category.models import Category
from orders.models import Order, OrderProduct
from store.models import Product, VariationManager
from accounts.models import Account
from carts.views import _cart_id
from carts.models import Cart,CartItem
from django.contrib import messages , auth
from django.contrib.auth.decorators import login_required , user_passes_test
from django.contrib.auth import logout
from adminapp.forms import AddProductForm , AddCategoryForm , AddVariationForm ,ProductGalleryForm
from store.models import Variation
from django.template.loader import render_to_string
# from weasyprint import HTML
import tempfile
from django.db.models import Sum


# Create your views here.
def admin_login(request):
  if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email = email, password = password,is_admin=True)
        try:
          if user.is_superadmin:
            if user is not None:
                auth.login(request, user)
                request.session['key'] = "value"
                  #messages.success(request, "You are Successfully Logged in")
                messages.success(request, 'Admin Logged in successfully')
                return redirect('admin_dashboard')
          else:
              messages.error(request, 'You are not an Admin')
              return redirect('admin_login')
        except Exception as e:
          messages.error(request, 'You are not an Admin')      
  return render(request, 'admin/adminlogin.html')

@login_required(login_url = 'admin_login')
@user_passes_test(lambda user: user.is_superadmin)
def admin_dashboard(request):
  total_orders = OrderProduct.objects.filter(ordered=True).count()
  total_products = Product.objects.all().count()
  total_revenue = Order.objects.aggregate(Sum("order_total"))
  total_categories = Category.objects.all().count()
  cancel_count = OrderProduct.objects.filter(status = "Cancelled").count()
  new_count = OrderProduct.objects.filter(status = "New").count()
  delivered_count = OrderProduct.objects.filter(status = "Completed").count()
  print(delivered_count)
  print(new_count)
  print(cancel_count)
  context ={
    'total_orders': total_orders,
    'total_products': total_products,
    'total_revenue': total_revenue,
    'total_categories': total_categories,
    'order_status1': [new_count,delivered_count,cancel_count],

  }
  return render(request, 'admin/admindashboard.html',context)

@login_required(login_url = 'admin_login')
@user_passes_test(lambda user: user.is_superadmin)
def user_management(request): 
  users = Account.objects.all()
  context = {
    'users': users,
  }
  return render(request, 'admin/manage_user.html',context )

def delete_user(request,user_id):
    account = Account.objects.get(pk=user_id)
    account.delete()
    return redirect('user_management')

def block_user(request,user_id):
    account = Account.objects.get(pk=user_id)
    account.is_active = False
    account.save()
    return redirect('user_management')

def unblock_user(request,user_id):
    account = Account.objects.get(pk=user_id)
    account.is_active = True
    account.save()
    return redirect('user_management')

@login_required(login_url = 'admin_login')
@user_passes_test(lambda user: user.is_superadmin)
def product_management(request):
  products = Product.objects.all()
  context = {
    'products': products,
  }
  return render(request, 'admin/product_management.html',context) 

@login_required(login_url = 'admin_login')
@user_passes_test(lambda user: user.is_superadmin)
def category_management(request):
  categories = Category.objects.all()
  context = {
    'categories': categories,
  }
  return render(request, 'admin/category_management.html',context) 

def delete_category(request,category_id):
    category = Category.objects.get(pk=category_id)
    category.delete()
    return redirect('category_management')

@login_required(login_url = 'admin_login')
@user_passes_test(lambda user: user.is_superadmin)
def admin_logout(request):
  if request.session.has_key('key'):
    del(request.session['key'])
  messages.success(request , 'Logged Out Successfully')
  return redirect('admin_login')

def add_product(request):
  product_form = AddProductForm()
  
  if request.method == 'POST':
    product_form = AddProductForm(request.POST,request.FILES)

    if product_form.is_valid():

      product_form.save()

      messages.success(request, 'Product added')
      return redirect('product_management')

  else:
     product_form = AddProductForm()

  context ={
    'product_form': product_form,
       }
  return render(request, 'admin/add_product.html',context)

def delete_product(request,product_id):
    product = Product.objects.get(pk=product_id)
    product.delete()
    return redirect('product_management')


def edit_product(request,product_id):
  product = Product.objects.get(pk=product_id)
  product_form = AddProductForm(instance=product)
  if request.method == 'POST':
    product_form = AddProductForm(request.POST,request.FILES,instance=product) 
    if product_form.is_valid():
      product_form.save()
      

      messages.success(request, 'Product Details Changed')
      return redirect('product_management')
  context ={
    'product_form': product_form,
    'product' : product,
       }
  return render(request, 'admin/edit_product.html',context)



def add_category(request):
  category_form = AddCategoryForm()
  if request.method == 'POST':
    category_form = AddCategoryForm(request.POST,request.FILES)
    if category_form.is_valid():
      print("help")
      category_form.save()
      messages.success(request, 'Category added')
      return redirect('category_management')
  else:
    category_form = AddCategoryForm()
  
  context ={
    'category_form': category_form,
  }
  return render(request, 'admin/add_category.html', context)


def edit_category(request,category_id):
  category = Category.objects.get(pk=category_id)
  category_form = AddCategoryForm(instance=category)
  if request.method == 'POST':
    category_form = AddCategoryForm(request.POST,request.FILES,instance=category) 
    if category_form.is_valid():
      category_form.save()
      messages.success(request, 'Category Details Changed')
      return redirect('category_management')

  context ={
    'category_form': category_form,
    'category' : category,
       }
  return render(request, 'admin/edit_category.html',context)

@login_required(login_url = 'admin_login')  
@user_passes_test(lambda user: user.is_superadmin)
def variation_management(request):
    variations = Variation.objects.all()
   
    context ={
        'variations' : variations,
    }
    return render(request, 'admin/variation_management.html', context)

def add_variation(request):
  variation_form = AddVariationForm()
  
  if request.method == 'POST':
    variation_form = AddVariationForm(request.POST,request.FILES)

    if variation_form.is_valid():

      variation_form.save()

      return redirect('variation_management')

  else:
     variation_form = AddVariationForm()

  context ={
    'variation_form': variation_form,
       }
  return render(request, 'admin/add_variation.html',context)

def edit_variation(request,product_id):
  print("hello1")
  variation = Variation.objects.get(pk=product_id)
  print("hello2")
  variation_form = AddVariationForm(instance=variation)
  print("hello3")
  if request.method == 'POST':
    print("hello4")
    variation_form = AddVariationForm(request.POST,request.FILES,instance=variation) 
    print("hello5")
    if variation_form.is_valid():
      print("hello6")
      variation_form.save()
      print("hello7")
      
      return redirect('variation_management')
  context ={
    'variation_form': variation_form,
    'variation' : variation,
       }
  return render(request, 'admin/edit_variation.html',context)

def delete_variation(request,product_id):
    variation = Variation.objects.get(pk=product_id)
    variation.delete()
    return redirect('variation_management')

def order_management(request,):
    orders = Order.objects.all()
    context = {
        'orders': orders,
    }
    return render(request, 'admin/order_management.html', context)

def placed(request,order_id):
    order = Order.objects.get(pk=order_id)
    order.status = "Order Placed"
    order.save()
    context ={
      'order' : order,
    }
    return redirect('order_management')

def cancelled(request,order_id):
    order = Order.objects.get(pk=order_id)
    order.status = "Order Cancelled"
    order.save()
    context ={
      'order' : order,
    }
    return redirect('order_management')

def delivered(request,order_id):
    order = Order.objects.get(pk=order_id)
    order.status = "Order Delivered"
    order.save()
    context ={
      'order' : order,
    }
    return redirect('order_management')

def product_reports(request):
    products = Product.objects.all()
    context ={
      'products' : products,
    }
    return render(request, 'admin/reports.html',context)

def sales_report(request):
    orders = Order.objects.all()
    context ={
      'orders' : orders,
    }
    return render(request, 'admin/salesreport.html',context)

def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename="productprint.pdf'

    response['Content-Transfer-Encoding'] = 'binary'
    products = Product.objects.all()

    html_string = render_to_string(
        'admin/productprint.html',{'products': products, 'total':0 })
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        #output = open(output.name, 'rb')
        output.seek(0)
        response.write(output.read())

    return response


def exportsales_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename="salesprint.pdf'

    response['Content-Transfer-Encoding'] = 'binary'
    orders = Order.objects.all()

    html_string = render_to_string(
        'admin/salesprint.html',{'orders': orders, 'total':0 })
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        #output = open(output.name, 'rb')
        output.seek(0)
        response.write(output.read())

    return response

def addproductgallery(request):
    form = ProductGalleryForm()

    if request.method == "POST":
        form = ProductGalleryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("productlists")

    context = {"form": form}
    return render(request, "adminapp/addproductgallery.html", context)