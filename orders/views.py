from ast import Or
from itertools import product
from multiprocessing import context
from django.shortcuts import render , redirect
from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, OrderProduct, Payment
import datetime
from store.models import Product
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.urls import reverse

#razorpay

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

# Create your views here.

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def place_order(request ,total = 0, quantity = 0,):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax 

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            #Store all the billing information inside Order table
            data = Order()
            data.user = current_user
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

            #generate order number

            yr=int(datetime.date.today().strftime('%Y'))
            dt=int(datetime.date.today().strftime('%d'))
            mt=int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20220809
            currency = 'INR'
            amount = grand_total * 100
            request.session['razorpayamount'] = amount
            razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))
            order_number = razorpay_order['id']
            data.order_number = razorpay_order['id']
            data.save()

            razorpay_order_id = razorpay_order['id']
            callback_url = 'paymenthandler/'

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
                
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
                'razorpay_order_id' : razorpay_order_id,
                'razorpay_merchant_key' : settings.RAZOR_KEY_ID,
                'razorpay_amount' : amount, 
                'callback_url' : callback_url
            }
            return render(request, 'orders/payments.html', context) 
        else:
            return redirect('checkout')


@csrf_exempt
def paymenthandler(request):
 
    # only accept POST request.
    if request.method == "POST":
        try:
           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                amount = request.session['razorpayamount']
                try:
                    order = Order.objects.get(user=request.user, is_ordered=False, order_number=razorpay_order_id)
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)

                    payment = Payment(
                        user=request.user,
                        payment_id = payment_id,
                        payment_method = 'razorpay',
                        amount_paid = order.order_total,
                        status = 'completed',
                    )
                    payment.save()

                    order.payment = payment
                    order.is_ordered = True
                    order.save()
                    

                    cart_items = CartItem.objects.filter(user=request.user)
                    for item in cart_items:
                        orderproduct = OrderProduct()
                        orderproduct.order_id = order.id
                        orderproduct.payment = payment
                        orderproduct.user_id = request.user.id
                        orderproduct.product_id = item.product_id
                        orderproduct.quantity = item.quantity
                        orderproduct.product_price = item.product.price
                        orderproduct.ordered = True
                        orderproduct.save()


                        # cart_item = CartItem.objects.get(id=item.id)
                        # product_variation = cart_item.variations.all()
                        # orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                        # orderproduct.variations.set(product_variation)
                        # orderproduct.save()


                        # reduce the quantity of the sold products
                        product = Product.objects.get(id=item.product_id)
                        product.stock -= item.quantity
                        product.save()

                    #clear cart
                    CartItem.objects.filter(user=request.user).delete()
                    #send recieved email to customer
                    # mail_subject = 'Thank You For Your Order'
                    # message = render_to_string('orders/order_recieved_email.html',{
                    #     'user' : request.user,
                    #     'order' : order,
                    # })
                    # to_email = request.user.email
                    # send_email = EmailMessage(mail_subject, message,to=[to_email])
                    # send_email.send()
                    # print('test mail')

                    param = (
                        "order_number="+ order.order_number +"&payment_id=" + payment.payment_id
                    )

                    # Capture the payment
                    redirect_url = reverse("order_complete")
                    return redirect(f"{redirect_url}?{param}")
                except Exception as e:
                    raise e
                    # if there is an error while capturing payment.
                    return render(request, 'orders/paymentfail.html')
            else:
 
                # if signature verification fails.
                
                return render(request, 'orders/paymentfail.html')
        except Exception as e:
            raise e
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()

def order_complete(request):
    print('testing')
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')

    try:
        print('hello')
        order = Order.objects.get(order_number=order_number,is_ordered = True)
        ordered_products = OrderProduct.objects.filter(order_id = order.id)
    

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id = payment_id)

        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number' : order.order_number,
            'payment_id' : payment.payment_id,
            'payment' : payment,
            'subtotal' : subtotal,
        }
        return render(request, 'orders/order_complete.html',context)
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

