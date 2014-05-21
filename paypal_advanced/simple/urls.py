from django.conf.urls.defaults import *
from django.conf.urls import patterns, include, url
#import paypal_advanced
#from paypal_advanced import urls
from django.contrib import admin
admin.autodiscover()


from satchmo_store.urls import urlpatterns

urlpatterns += patterns('',
    (r'test/', include('simple.localsite.urls')),
    #url(r'^payment_pay/$', include(paypal_advanced.urls)),
    url(r'^paypal_advanced/', include('paypal_advanced.urls')),
    url(r'^payment_success/', 'paypal_advanced.views.payment_success', name='payment_success'),
    
    url(r'^admin/', include(admin.site.urls)),
    
)
