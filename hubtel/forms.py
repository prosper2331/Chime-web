from django import forms
class VerifyForm(forms.Form):
    code1 = forms.CharField(max_length=255)
    code2 = forms.CharField(max_length=255)
    code3 = forms.CharField(max_length=255)
    code4 = forms.CharField(max_length=13)