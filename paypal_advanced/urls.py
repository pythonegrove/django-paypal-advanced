from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'paypal_advanced.views.home', name='home'),
    url(r'^payment_success/', 'paypal_advanced.views.payment_success', name='payment_success'),
)
