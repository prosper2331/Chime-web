from django.db import models
from account.models import Customer
class User_otp(models.Model):
    user = models.ForeignKey(Customer,on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    request_id = models.CharField(max_length=50)
    prefix = models.CharField(max_length=50)
    
    def __str__(self):
        return self.code