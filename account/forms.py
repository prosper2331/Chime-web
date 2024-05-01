from django import forms
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm)

from .models import Customer
import re


class UserLoginForm(AuthenticationForm):

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control mb-3', 'placeholder': 'Username', 'id': 'login-username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'login-pwd',
        }
    ))


class RegistrationForm(forms.ModelForm):
    COUNTRY_CHOICES = [
        ('US', 'USA'),
        ('CA', 'Canada'),
        ('DE', 'Germany'),
        ('AU', 'Australia'),
        #('GH', 'Ghana'),
    ]

    user_name = forms.CharField(label='Username', min_length=4, max_length=50, help_text='Required', required=False)
    mobile = forms.CharField(label='Phone Number', min_length=10, max_length=14, help_text='Required')
    email = forms.EmailField(max_length=100, help_text='Required', error_messages={'required': 'Sorry, you will need an email'})
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)
    country_choice = forms.ChoiceField(label='Select Country', choices=COUNTRY_CHOICES)

    # Rest of the form code...


    class Meta:
        model = Customer
        fields = ('user_name', 'email','mobile')

    def clean_username(self):
        user_name = self.cleaned_data['user_name']
        r = Customer.objects.filter(user_name=user_name)
        if r.count():
            raise forms.ValidationError("Username already exists")
        return user_name

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords do not match.')
        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Please use another Email, that is already taken')
        return email
    
    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        if not re.match(r'^\d+$', mobile):
            raise forms.ValidationError('Please neglect country code or any brackets')
        return mobile

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_name'].widget.attrs.update(
            {'class': 'input-field', })
        self.fields['email'].widget.attrs.update(
            {'class': 'input-field',  'name': 'email', 'id': 'id_email'})
        self.fields['password'].widget.attrs.update(
            {'class': 'input-field', })
        self.fields['password2'].widget.attrs.update(
            {'class': 'input-field', })
        self.fields['mobile'].widget.attrs.update(
            {'class': 'input-field', })
        self.fields['country_choice'].widget.attrs.update(
            {'class': 'class="block px-4 items-center w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6', })


class PwdResetForm(PasswordResetForm):

    email = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'input', 'placeholder': 'Email', 'id': 'form-email'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        u = Customer.objects.filter(email=email)
        if not u:
            raise forms.ValidationError(
                'Unfortunatley we can not find that email address')
        return email


class PwdResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password', widget=forms.PasswordInput(
            attrs={'class': 'input-field',  'id': 'form-newpass'}))
    new_password2 = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput(
            attrs={'class': 'input-field',  'id': 'form-new-pass2'}))


class UserEditForm(forms.ModelForm):

    email = forms.EmailField(
        label='Account email (can not be changed)', max_length=200, widget=forms.TextInput(
            attrs={'class': 'input-field active', 'placeholder': 'email', 'id': 'form-email', 'readonly': 'readonly'}))

    user_name = forms.CharField(
        label='Username', min_length=3, max_length=50, widget=forms.TextInput(
            attrs={'class': 'input-field active', 'placeholder': 'Username', 'id': 'form-user-name', }))


    class Meta:
        model = Customer
        fields = ('email', 'user_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_name'].required = True
        self.fields['email'].required = True
