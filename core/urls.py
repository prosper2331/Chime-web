from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('prince/admin/', admin.site.urls),
    path('', include('store.urls')),
    path('verify/', include('hubtel.urls')),
    path('account/', include('account.urls', namespace="account")),
    path('pay/', include('payment.urls', namespace="payment")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)