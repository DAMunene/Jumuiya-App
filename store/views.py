from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.http import JsonResponse, HttpResponse, HttpRequest
import json
import datetime
from .import forms
from django.contrib import messages
from django.conf import settings


def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()       
        cartItems = order.get_cart_items
    else:
        items= []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping':False}       
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    context = {'products': products,'cartItems':cartItems }
    return render(request, 'store/store.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        
    else:
        items=[]
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping':False}
        cartItems = order['get_cart_items']

    context = {'items':items, 'order': order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        
    else:
        # Create empty cart for non-logged in user
        items=[]
        
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping':False}
        cartItems = order['get_cart_items']

    context = {'items':items, 'order': order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

def initiate_payment(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        payment_form = forms.PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save()
            return render( request, 'store/make_payment.html', {'payment': payment, 'paystack_public_key':settings.PAYSTACK_PUBLIC_KEY })
    else:
        payment_form = forms.PaymentForm()

    return render(request, 'store/initiate_payment.html', {'payment_form': payment_form})


def verify_payment(request:HttpRequest, ref:str) -> HttpResponse:
    payment = get_object_or_404(Payment, ref=ref)
    verified = payment.verify_payment()
    if verified:
        messages.success(request, "Verification Successful")
        return redirect('store')

    else:
        messages.error(request, "Verification Failed")
    return redirect('initiate_payment')



    


def updateItem(request):    
    data = json.loads(request.body)
    productId = data ['productId']
    action = data ['action']
    print('Action:' ,action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order,created = Order.objects.get_or_create( customer=customer, complete=False)

    orderItem,created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):   
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create( customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id  = transaction_id

        if total == float(order.get_cart_total):
            order.complete = True
            order.save()
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order=order,
                address= data['shipping']['address'],
                town= data['shipping']['town'],
                county= data['shipping']['county'],
                postalcode= data['shipping']['postalcode'],
            )
    else:
        print('User is not logged in..')

    return JsonResponse('Payment complete!', safe=False)


    
