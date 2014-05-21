from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.utils.translation import ugettext, ugettext_lazy as _


TRANSACTION_MODE_CHOICES = (
    ('Sandbox', 'Sandbox'),
    ('Live', 'Live'),
)

class TransactionProcessMode(models.Model):
    mode = models.CharField(max_length=200, choices=TRANSACTION_MODE_CHOICES, default="Sandbox")
    URL = models.URLField(max_length=500, help_text="Sanddbox: https://pilot-payflowpro.paypal.com and Live: https://payflowpro.paypal.com")
    
    def __unicode__(self):
        return self.mode
    
    
class CurrencySettings(models.Model):
    name = models.CharField(max_length=200, default="Australian Dollar", help_text="Ex: U.S. Dollar - USD, Singapore Dollar - SGD")
    currency_code = models.CharField(max_length=10, default="AUD", help_text="Ref: https://cms.paypal.com/mx/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_nvp_currency_codes")

    def __unicode__(self):
        return self.name + '-' + self.currency_code    
    

class MerchantAccountSettings(models.Model):
    partner = models.CharField(max_length=200, help_text="Payflow partner")
    vendor = models.CharField(max_length=200, help_text = "Merchant Login ID that you use to log into PayPal Manager")
    paypal_user = models.CharField(max_length=200, help_text="The name of the user whom you added to your account using PayPal Manager")
    paypal_password = models.CharField(max_length=200)
    currency = models.ForeignKey(CurrencySettings)
    
    def __unicode__(self):
        return self.paypal_user
    
    
IFRAME_SCROLLOING_CHOICES = (
    ('Yes', 'Yes'),
    ('No', 'No'),
)

class IframeSettings(models.Model):
    height = models.CharField(max_length=200, default='575',  help_text="Height of the iframe")
    width = models.CharField(max_length=200, default='570', help_text = "Width of the iframe")
    scrolling = models.CharField(max_length=200, choices=IFRAME_SCROLLOING_CHOICES, default='No', blank=True, null=True)
    
    def __unicode__(self):
        return self.height + '-' + self.width


ORDER_STATUS = (
    ('In Process', 'In Process'),
    ('Complete', 'Complete'),
    ('Refud', 'Refund'),
    ('Void', 'Void'),
    ('Cancelled', 'Cancelled'),
    )
    
    
class CheckOutDetails(models.Model):
    """
    Orders contain a copy of all the information at the time the order was
    placed.
    """
    first_name = models.CharField(max_length=100, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=100, verbose_name=_('Last Name'))
    email = models.EmailField(verbose_name=_("Email"))
    ship_street = models.CharField(verbose_name=_("Street"), max_length=80)
    ship_city = models.CharField(verbose_name=_("City"), max_length=50)
    ship_state = models.CharField(verbose_name=_("State"), max_length=50)
    ship_postal_code = models.CharField(verbose_name=_("Zip Code"), max_length=30)
    ship_country = models.CharField(verbose_name=_("Country"), max_length=20)
    notes = models.TextField(verbose_name=_("Notes"), blank=True, null=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2)
    tax = models.DecimalField(max_digits=8, decimal_places=2)
    order_created_time = models.DateTimeField(verbose_name=_("Created Time"), auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_("Last Updated"), auto_now=True)
    status = models.CharField(verbose_name=_("Status"), max_length=20, choices=ORDER_STATUS,
        blank=True, help_text=_("This is set automatically."))
    phone = models.CharField(verbose_name="Phone", max_length=15)
    invoice_number = models.CharField(verbose_name="Invoice Number", max_length=50, )
    
    

    def __unicode__(self):
        return self.first_name + '-' + self.last_name    


class CheckoutForm(ModelForm):
    class Meta:
        model = CheckOutDetails
        exclude = ['status', 'notes', 'update_time', 'order_created_time']
        

class TransactionStatus(models.Model):
    #user passed values
    order_id = models.CharField(verbose_name="Order ID", max_length=20)
    invoice_number = models.CharField(verbose_name="Invoice Number", max_length=50, )
    #Paypal response values
    transaction_id = models.CharField(verbose_name="Transaction ID", max_length=50)
    amount = models.DecimalField(verbose_name="Amount", max_digits=8, decimal_places=2)
    status = models.CharField(verbose_name="Transaction Status", max_length=200)
    timestamp = models.DateTimeField(verbose_name="Transaction Time")
    notes = models.TextField(verbose_name="Notes")
    
    
    def __unicode__(self):
        return self.order_id + '-' + self.status
        
        

    
    