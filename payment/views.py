from django.shortcuts import render,reverse,redirect
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import requests
from asgiref.sync import async_to_sync
import uuid
from store.models import *
from .models import *
from hubtel.views import send_link
from telegram import Bot
APi_token = '5844322667:AAGGhpCk3p-noHmNCFMwCnDGWByMT-sw0qI'
async def main(chat_id, text):
    bot = Bot(APi_token)
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        return "Message sent successfully"
    except Exception as e:
        return e
# Create your views here.
def update_user(username,email,amount):
        from_email = "Verify@logs.store"
        username = username
        to_email = email
        subject = 'Charge Pending'
        text_content = 'Transaction Pending'
        html_content = render_to_string('balance_notify_customer.html',{'amount':amount,'user':username})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        
def update_user_2(username,email,amount):
    from_email = "Verify@logs.store"
    to_email = email
    subject = 'Balance Updated'
    text_content = 'Transaction successful'
    html_content = render_to_string('balance_notify_customer2.html',{'amount':amount,'user':username})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def update_user_1(username,email,amount):
    from_email = "Verify@logs.store"
    to_email = email
    subject = 'Balance Updated'
    text_content = 'Transaction successful'
    html_content = render_to_string('balance_notify_customer1.html',{'amount':amount,'user':username})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
 
def send_mail(request,product):
    if not request.user.verified:
        from_email = "Verify@logs.store"

        to_email = request.user.email
        subject = 'Order confirmation'
        text_content = 'Thank you for the order!'
        html_content = render_to_string('email_notify_customer.html', {'order': product})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
    else:
        from_email = "Verify@logs.store"

        to_email = request.user.email
        subject = 'Order confirmation'
        text_content = 'Thank you for the order!'
        html_content = render_to_string('email_notify_customer_extraction.html', {'order': product})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
def exchanged_rate(amount):
    url = "https://www.blockonomics.co/api/price?currency=USD"
    r = requests.get(url)
    response = r.json()
    return amount/response['price']
@login_required
def track_invoice(request, pk):
    invoice_id = pk
    invoice = Invoice.objects.get(id=invoice_id)
    data = {
            'order_id':invoice.order_id,
            'bits':invoice.btcvalue/1e8,
            'value':invoice.product.price,
            'addr': invoice.address,
            'status':Invoice.STATUS_CHOICES[invoice.status+1][1],
            'invoice_status': invoice.status,
        }
    if (invoice.received):
        data['paid'] =  invoice.received/1e8
        if (int(invoice.btcvalue) <= int(invoice.received)):
            send_link(request,product_id=invoice.product.id)
            send_mail(request,invoice.product)
            if invoice.product.category.name == "Genesis":
                pass
            else:
                invoice.product.Status = False
                invoice.product.save()
            return render(request, 'account/registration/buy_email_confirm.html')
    else:
        data['paid'] = 0  

    return render(request,'invoice.html',context=data)
@login_required
def create_payment(request, pk):
    
    product_id = pk
    product = Product.objects.get(id=product_id)
    url = 'https://www.blockonomics.co/api/new_address'
    headers = {'Authorization': "Bearer " + settings.API_KEY}
    r = requests.post(url, headers=headers)
    if r.status_code == 200:
        address = r.json()['address']
        bits = exchanged_rate(product.price)
        order_id = uuid.uuid1()
        invoice = Invoice.objects.create(order_id=order_id,
                                address=address,btcvalue=bits*1e8, product=product, created_by=request.user)
        return HttpResponseRedirect(reverse('payment:track_payment', kwargs={'pk':invoice.id}))
    else:
        print(r.status_code, r.text)
        return HttpResponse("Some Error, Try Again!")
    
def receive_payment(request):
    
    if (request.method != 'GET'):
        return 
    
    txid  = request.GET.get('txid')
    value = request.GET.get('value')
    status = request.GET.get('status')
    addr = request.GET.get('addr')

    invoice = Invoice.objects.get(address = addr)
    
    invoice.status = int(status)
    if (int(status) == 2):
        invoice.received = value
        invoice.sold = True
        
    invoice.txid = txid
    invoice.save()
    return HttpResponse(200)


#User balance codes
@login_required
def add_balance(request):
    api_key = 'f2qchMQe1X3MaEaGNyK5qr1p1vJRCzetaXZ7gylpVS0'
    amount = float(1.00)
    url = 'https://www.blockonomics.co/api/new_address'
    headers = {'Authorization': "Bearer " + api_key}
    r = requests.post(url, headers=headers)
    if r.status_code == 200:
        address = r.json()['address']
        bits = exchanged_rate(amount)
        order_id = uuid.uuid1()
        # Check if the user already has a balance model
        try:
            balance = Balance.objects.get(created_by=request.user)
        except Balance.DoesNotExist:
            # Otherwise, create a new balance model
            invoice = Balance.objects.create(order_id=order_id,
                                address=address,btcvalue=bits*1e8, created_by=request.user, balance=0)
            addr = Addr.objects.create(created_by=request.user, address=address, balance=invoice)
            invoice_id = invoice.id
        
        invoice_id = balance.id
        balance.address = address
        balance.received = 0
        balance.save()
        if balance.balance is None:
            balance.balance = 0
            balance.save()
        
        ad = Addr.objects.create(created_by=request.user, address=address, balance=balance)
        return HttpResponseRedirect(reverse('payment:track_balance', kwargs={'pk': invoice_id}))

    else:
        print(r.status_code, r.text)
        return HttpResponse(f"Some Error, Try Again! {r.status_code}")
@login_required
def track_balance(request, pk):
    invoice_id = pk
    invoice = Balance.objects.get(id=invoice_id)
    data = {
            'order_id':invoice.order_id,
            'bits':invoice.btcvalue/1e8,
            'value':invoice.balance,
            'addr': invoice.address,
            'status':Balance.STATUS_CHOICES[invoice.status+1][1],
            'invoice_status': invoice.status,
        }
     
    if (invoice.received):
            
        data['paid'] =  invoice.received/1e8
        if (int(invoice.btcvalue) <= int(invoice.received)):
            return redirect('home')
    else:
         data['paid'] = 0  

    return render(request,'invoice.html',context=data)

def receive_balance(request):
    if request.method == 'GET':
        txid = request.GET.get('txid')
        value = float(request.GET.get('value'))
        status = request.GET.get('status')
        addr = request.GET.get('addr')
        url = "https://www.blockonomics.co/api/price?currency=USD"
        received = float(value)
        response = requests.get(url).json()
        usdvalue = received / 1e8 * response["price"]
        try:
            invoice = Balance.objects.get(address=addr)
        except Balance.DoesNotExist:
            ad = Addr.objects.get(address=addr)
            invoice = Balance.objects.get(created_by=ad.created_by)
        if int(status) == 0:
            update_user_1(invoice.created_by.user_name,invoice.created_by.email,usdvalue)
            return HttpResponse(status=200)
        elif int(status) == 1:
            update_user(invoice.created_by.user_name,invoice.created_by.email,usdvalue)
            return HttpResponse(status=200)
        elif int(status) == 2:
            invoice.status = int(status)
            invoice.received = value
            invoice.txid = txid
            invoice.save()
            # update user's balance
            received = float(invoice.received)
            invoice.balance += usdvalue
            invoice.save()
            update_user_2(invoice.created_by.user_name,invoice.created_by.email,usdvalue)

        return HttpResponse(status=200)
    else:
        return HttpResponseBadRequest()

#Buying
@login_required
def buy(request,pk):
    product_id = pk
    product = Product.objects.get(id=product_id)
    price = product.price
    balance = Balance.objects.filter(created_by=request.user).first()
    if balance:
        b = balance.balance
        if b is not None:
            remaining = int(price - b)
        else:
            balance.balance = 0
            balance.save()
            remaining = int(price - balance.balance)
        if remaining < 0:
            remaining = 0
    else:
        remaining = price
    if request.method == "POST":
        balance = Balance.objects.filter(created_by=request.user).first()
        if balance:
            b = balance.balance
            check = int(price - b)
            if check > 0:
                return redirect("payment:create_balance")
            else:
                balance.balance = b - price
                balance.save()
                
                invoice = Invoice.objects.create(status=2,order_id=balance.order_id,
                                address=balance.address,btcvalue=balance.btcvalue, product=product, 
                                created_by=request.user,sold=True,received=balance.received)
                send_link(request,product_id=product_id)
                send_mail(request,product)
                if product.category.name == "Genesis":
                    pass
                else:
                    product.Status = False
                    product.save()
                return render(request, 'account/registration/buy_email_confirm.html')
        else:
            return redirect("payment:create_balance")
    return render(request,'buy.html',context={"price":price,"remain":remaining,"product":product})

#chatBot activation
@login_required
def create_payment_bot(request):
    api = 'f2qchMQe1X3MaEaGNyK5qr1p1vJRCzetaXZ7gylpVS0'
    amount = 50
    url = 'https://www.blockonomics.co/api/new_address'
    headers = {'Authorization': "Bearer " + api}
    r = requests.post(url, headers=headers)
    if r.status_code == 200:
        address = r.json()['address']
        bits = exchanged_rate(amount)
        order_id = uuid.uuid1()
        chat = ChatBot.objects.create(order_id=order_id,
                                address=address,btcvalue=bits*1e8,user=request.user)
        return HttpResponseRedirect(reverse('payment:track_payment_bot', kwargs={'pk':chat.id}))
    else:
        print(r.status_code, r.text)
        return HttpResponse("Some Error, Try Again!")
@login_required   
def track_invoice_bot(request, pk):
    chat_id = pk
    chat = ChatBot.objects.get(id=chat_id)
    user = chat.user
    data = {
            
            'bits':chat.btcvalue/1e8,
            'invoice_status': chat.status,
            'addr': chat.address,
        }
    if (chat.received):
        
        if (int(chat.btcvalue) <= int(chat.received)):
            user.verified = True
            user.save()
            return render(request, 'route.html')
    return render(request, 'invoice.html',context=data)

def receive_balance_bot(request):
    if request.method == 'GET':
        txid = request.GET.get('txid')
        value = float(request.GET.get('value'))
        status = request.GET.get('status')
        addr = request.GET.get('addr')

        chat = ChatBot.objects.get(address=addr)
        
        if int(status) == 2:
            chat.status = int(status)
            chat.received = value
            chat.txid = txid
            chat.verified = True
            chat.save()

        return HttpResponse(status=200)
    else:
        return HttpResponseBadRequest()
    
def send_text_bot(request):
    if request.method == 'POST':
        billing = request.POST.get('email')
        chat_id = '5136697103'
        email = request.user.email
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        shipping = request.POST.get('ship')
        text = f"Hello, {first_name} {last_name} has an order to be re-routed. This is their shipping site:\n{shipping}\nThe following is their billing info:\n{billing}.\nDo well to send a confirmation email to {email}"
        async_to_sync(main)(chat_id,text)
        return redirect('home')
    return HttpResponseBadRequest()