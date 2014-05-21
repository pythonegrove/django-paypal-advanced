django-paypal-advanced
======================


### Django application for PayPal Advanced integration


This is a fairly simple paypal-advanced application for Django,
designed to make allowing user to make payments as painless as possible. It
requires a functional installation of Django 1.4 or newer, but has no  but has no
other dependencies.


*  Download and install the django paypal_advanced module:

```pip install -e git+https://github.com/developerpython/django-paypal-advanced.git```

      
*  Then,add the module in the Installed_apps section in your `settings.py`:

```
INSTALLED_APPS = (
    ...
    
    'paypal_advanced',
)
```
  
* Import paypal_advanced,and archive URL's somewhere in your `urls.py`:
    
```
urlpatterns = patterns('',
	(r'^paypal_advanced/', include('paypal_advanced.urls')),
		
)
```


*  Create required data structure:
```./manage.py syncdb```
