from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

admin.site.site_title = 'KiLib-Bookstore'
admin.site.site_header = 'KiLib-Bookstore'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls', namespace='store')),
    path('basket/', include('basket.urls', namespace='basket')),
    path('account/', include('accounts.urls', namespace='accounts')),
    path('pay/', include('payment.urls', namespace='payment')),
    path('wallet/', include('wallet.urls', namespace='wallet')),
    path('contact-us/', include('contact.urls', namespace='contact')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)