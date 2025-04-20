from django.shortcuts import render
from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from orders.models import Order
from decimal import Decimal


#def index(request):
cl = MpesaClient()
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
#    phone_number = '0743192968'
#    amount = 1
#    account_reference = 'reference'
#    transaction_desc = 'Description'
#    callback_url = 'https://darajambili.herokuapp.com/express-payment';
#    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
#    return HttpResponse(response)

def stk_push_callback(request):
        data = request.body
        
        return HttpResponse("STK Push in Django👋")

def pesa_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))

        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

    # Mpesa checkout session data
        session_data = {
#        'mode': 'payment',
#        'client_reference_id': order.id,
#        'success_url': success_url,
#        'cancel_url': cancel_url,
#        'line_items': []
            'phone_number': '0743192968',
            'amount': 1,
            'account_reference': 'reference',
            'transaction_desc': 'Description',
            'callback_url': 'https://darajambili.herokuapp.cont'
        }
    # create Mpesa checkout session
        session = cl.stk_push(**session_data)
# redirect to Stripe payment form
        return redirect(session.url, code=303)

    else:
        return render(request, 'payment/process.html')

def payment_completed(request):
        return render(request, 'payment/completed.html')


def payment_canceled(request):
        return render(request, 'payment/canceled.html')
