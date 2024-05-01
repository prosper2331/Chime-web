import requests
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User_otp
from .forms import VerifyForm
from django.http import JsonResponse,HttpResponse
import json
from django.contrib.auth import login
from account.models import *
from django.contrib.auth.decorators import login_required
from store.models import *
from account.tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
def send_otp(request, users, phone_number):
    use = users
    username = 'jjkyikvp'
    password = 'ujtwatej'
    sender_id = 'Verify_logs'
    country_code = 'GH'

    if phone_number.startswith('+1'):
        country_code = 'US'
    elif phone_number.startswith('+49'):
        country_code = 'DE'
    elif phone_number.startswith('+61'):
        country_code = 'AU'
    url = 'https://api-otp.hubtel.com/otp/send'

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'senderId': sender_id,
        'phoneNumber': phone_number,
        'countryCode': country_code
    }

    response = requests.post(url, headers=headers, json=data, auth=(username, password))
    response_data = response.json()

    if response.status_code == 200:
        code = response_data['code']
        requestId = response_data['data']['requestId']
        prefix = response_data['data']['prefix']
        existing_otp = User_otp.objects.filter(user=users)
        if existing_otp.exists():
            existing_otp = existing_otp.first()
            existing_otp.request_id = requestId
            existing_otp.prefix = prefix
            existing_otp.save()
        else:
            otp = User_otp.objects.create(user=use, code=code, request_id=requestId, prefix=prefix)
        
        return True
    else:
        send_activation_link_via_sms(request, users)
        
        return False



def otp_form(request):
    if request.method == "POST":
        form = VerifyForm(request.POST)
        if form.is_valid():
            code1 = str(form.cleaned_data['code1'])
            code2 = str(form.cleaned_data['code2'])
            code3 = str(form.cleaned_data['code3'])
            code4 = str(form.cleaned_data['code4'])
            otp_code = str(code1+code2+code3+code4)

            # Check if user is logged in
            if request.user.is_authenticated:
                user = request.user
            else:
                user_id = request.session.get('user_id')  # Retrieve user ID from session
                if user_id:
                    try:
                        user = Customer.objects.get(id=user_id)
                    except Customer.DoesNotExist:
                        user = None
                else:
                    user = None

            if verify_otp(otp_code, user):
                user.is_active = True
                user.save()
                login(request,user)
                
                del request.session['user_id']  # Clear the user ID from session if anonymous user
                return redirect("home")
            else:
                messages.error(request, "Incorrect OTP or Number not Supported. Please Request for SMS Verification.")
                return redirect("otp_form")
    else:
        form = VerifyForm()
    return render(request, "verify.html", {"form": form})



def verify_otp(otp_code, user):
    
    use = User_otp.objects.get(user=user)
    request_id = use.request_id
    otp_code = otp_code
    prefix = use.prefix
    
    # Set the authentication credentials for Hubtel OTP API
    username = 'jjkyikvp'
    password = 'ujtwatej'
        
    auth = (username, password)

    # Build the OTP verification request data
    data = {
        'requestId': request_id,
        'prefix': prefix, # replace with the prefix value returned in the OTP send request
        'code': otp_code,
    }
    headers = {'Content-Type': 'application/json'}

    # Make the OTP verification request to Hubtel OTP API
    response = requests.post('https://api-otp.hubtel.com/otp/verify', auth=auth, json=data, headers=headers)
    
    if response.status_code == 200:
        return True
    else:
        return False


def resend_otp(request):
    # Get the API username and password from your settings or environment variables
    username = 'jjkyikvp'
    password = 'ujtwatej'
    
    user = request.user
    otp = User_otp.objects.get(user=user)
    # Set the API endpoint URL
    url = 'https://api-otp.hubtel.com/otp/resend'
    
    # Set the request data
    data = {
        "requestId": otp.request_id
    }
    print(otp.request_id)
    # Set the request headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Send the request with Basic authentication
    response = requests.post(url, json=data, headers=headers, auth=(username, password))
    
    # Check the response status code
    response_data = response.json()
    if response.status_code == 200:
        requestId = response_data['data']['requestId']
        otp.request_id=requestId
        otp.save()
        return redirect('otp_form')
    else:
        print (response_data["message"])
        return JsonResponse({'error': 'Failed to resend OTP'})


def send_activation_link_via_sms(request,users):
    url = 'https://smsc.hubtel.com/v1/messages/send'
    username = 'jjkyikvp'
    password = 'ujtwatej'
    sender_id = 'Verify_logs'
    phone_number = str(users.mobile)
    user = users
    
    current_site = get_current_site(request)
    activation_link = 'http://{0}{1}'.format(current_site.domain,reverse('account:activate', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)), 'token': account_activation_token.make_token(user)})
    )

    message = 'Hi {0}, Your account has successfully been created. Please click the link below to activate your account: {1}'.format(user.user_name, activation_link)

    data = {
        'from': sender_id,
        'to': phone_number,
        'content': message
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), auth=(username, password))

    if response.status_code == 201:
        # handle success
        return True
    else:
        # handle error
        return False

def send_link(request,product_id):
    product = Product.objects.get(id=product_id)
    url = 'https://smsc.hubtel.com/v1/messages/send'
    username = 'jjkyikvp'
    password = 'ujtwatej'
    sender_id = 'Verify_logs'
    phone_number = str(request.user.mobile)
    user = request.user
    activation_link = product.pdf.url
    if product.premium:
        message = 'Hi {0}, Your purchase of {2} log has been processed successfully. Please click the link below to download a PDF containing all necessary information about the logs {1}. If access is restricted, press on this link to access a decryptor "https://ams3.digitaloceanspaces.com/megacash/media/pdfs/Extraction.pdf?AWSAccessKeyId=DO00C4HYQD6X7D24X78G&Signature=D4EwpbY7rHie2UcSUTwNDOp0%2F2w%3D&Expires=1683035913 ". Text your chatbot for tutorials as well.'.format(user.user_name, activation_link, product.name)
    elif product.category.name == "Extraction":
        message = 'Hi {0}, Your purchase of your {2} has been processed successfully. Please click the link below to download the PDF containing all necessary information about how to extract {1}'.format(user.user_name, activation_link, product.name)
    elif product.category.name == "Cards":
        message = 'Hi {0}, Your purchase of {2} has been processed successfully. Please click the link below to download a PDF containing all necessary information about the logs {1}. If access is restricted, press on this link to buy a decryptor "https://megacashouts.store/category/extraction"'.format(user.user_name, activation_link, product.name)
    else:
        message = 'Hi {0}, Your purchase of {2} log has been processed successfully. Please click the link below to download a PDF containing all necessary information about the logs {1}. If access is restricted, press on this link to buy a decryptor "https://megacashouts.store/category/extraction"'.format(user.user_name, activation_link, product.name)
    data = {
        'from': sender_id,
        'to': phone_number,
        'content': message
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), auth=(username, password))

    if response.status_code == 201:
        # handle success
        return render(request, 'account/registration/buy_email_confirm.html')
    else:
        # handle error
        return HttpResponse("Something went wrong")