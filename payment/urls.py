from django.urls import path
from . import views

app_name="payment"

urlpatterns=[
    path('create/<pk>', views.create_payment, name='create_payment'),
    path('unlock/bot', views.create_payment_bot, name='create_payment_bot'),
    path('invoice/<pk>',views.track_invoice, name='track_payment'),
    path('invoice/<pk>/bot',views.track_invoice_bot, name='track_payment_bot'),
    path('receive/', views.receive_payment, name='receive_payment'),
    path('buy/<int:pk>', views.buy, name='buy'),
    path('balance/create/', views.add_balance, name='create_balance'),
    path('balance/<int:pk>',views.track_balance, name='track_balance'),
    path('balance/receive/', views.receive_balance, name='receive_balance'),
    path('balance/receive/bot', views.receive_balance_bot, name='receive_balance_bot'),
    path('send/text/', views.send_text_bot, name='send_text')
]