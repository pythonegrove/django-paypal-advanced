from django.contrib import admin
from paypal_advanced.models import *
from daterange_filter.filter import DateRangeFilter


class TransactionProcessModeAdmin(admin.ModelAdmin):
    list_display = ('mode', 'URL')
    
    
class MerchantAccountSettingsAdmin(admin.ModelAdmin):
    list_display = ('partner', 'vendor', 'paypal_user', 'paypal_password', 'currency')
    
    
class IframeSettingsSettingsAdmin(admin.ModelAdmin):
    list_display = ('height', 'width', 'scrolling')
    
    
class CurrencySettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency_code')
    
    


class TransactionStatusAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'amount', 'transaction_id', 'status', 'timestamp')
    list_filter = ('order_id', ('timestamp', DateRangeFilter),'status', 'transaction_id', 'timestamp', 'amount')
    '''
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        try:
            extra_context['trade_date_gte'] = request.GET['date__gte']
        except:
            pass

        try:
            extra_context['trade_date_lte'] = request.GET['date__lte']
        except:
            pass

    
        return super(TransactionStatusAdmin, self).changelist_view(request, extra_context)  
'''






class CheckOutDetailsAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'total', 'shipping_cost', 'tax', 'order_created_time', 'status')
    list_filter = ('first_name', 'last_name', 'email', 'total', 'shipping_cost', 'tax', 'order_created_time', 'status')
    

admin.site.register(TransactionProcessMode, TransactionProcessModeAdmin)
admin.site.register(MerchantAccountSettings, MerchantAccountSettingsAdmin)
admin.site.register(IframeSettings, IframeSettingsSettingsAdmin)
admin.site.register(CurrencySettings, CurrencySettingsAdmin)
admin.site.register(CheckOutDetails, CheckOutDetailsAdmin)
admin.site.register(TransactionStatus, TransactionStatusAdmin)