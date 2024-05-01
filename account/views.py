from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.encoding import  force_str
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .forms import RegistrationForm
from .models import  Customer
from .tokens import account_activation_token
from hubtel.views import send_otp
from django.contrib.auth import login
from payment.models import *
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
@login_required
def dashboard(request):
    user = request.user
    invoice = Invoice.objects.filter(sold=True,created_by=user)
    data = {
        "products":invoice
    }
    return render(request, "account/user/dashboard.html", context=data)

def account_register(request):
    if request.method == "POST":
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            phone_number = registerForm.cleaned_data["mobile"]
            country_choice = registerForm.cleaned_data["country_choice"]
            
            if country_choice == 'US':
                phone_number = "+1" + phone_number
                user.mobile = phone_number
            elif country_choice == 'GH':
                phone_number = "+233" + phone_number
                user.mobile = phone_number
            elif country_choice == 'CA':
                phone_number = "+1" + phone_number
                user.mobile = phone_number
            if country_choice == 'DE':
                phone_number = "+49" + phone_number
                user.mobile = phone_number
            if country_choice == 'AU':
                phone_number = "+61" + phone_number
                user.mobile = phone_number

            user.email = registerForm.cleaned_data["email"]
            email = registerForm.cleaned_data["email"]
            user.user_name = registerForm.cleaned_data["user_name"]
            user.set_password(registerForm.cleaned_data["password"])
            user.is_active = False
            user.save()
            # Rest of the code...
            request.session['user_id'] = user.id
            users = Customer.objects.get(email=email)
            if send_otp(request,users,phone_number):
                return redirect("otp_form")
            else:
                return render(request, 'account/registration/register_email_confirm.html',{'mobile':user.mobile})
            
    else:
        registerForm = RegistrationForm()
    return render(request, "account/registration/signup.html", {"form": registerForm})


def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Customer.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
        user = None
        return HttpResponse("Activation invalidated. User account not found")
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("home")
    else:
        return HttpResponse("Activation invalid")

def send_activation_email(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user_id = request.session.get('user_id')
        # Retrieve user ID from session
        print(user_id)
        if user_id:
            try:
                user = Customer.objects.get(id=user_id)
                
            except Customer.DoesNotExist:
                user = None
                return HttpResponse("Problem with Signup. Contact chat support")
        else:
            user = None  # assuming the user is already registered
            return HttpResponse("Problem with Signup. Contact chat support")
    current_site = get_current_site(request)
    subject = 'Activate your Account'
    message = render_to_string('account/registration/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.id)),
        'token': account_activation_token.make_token(user),
    })
    from_email = 'Verify@logs.store'  # set your own email address here
    to_email = user.email
    send_mail(subject, message, from_email, [to_email], fail_silently=False)
    del request.session['user_id']
    return render(request, 'account/registration/done.html')
