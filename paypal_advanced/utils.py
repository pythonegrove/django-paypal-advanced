from django.conf import settings

def calculate_total_amount(amount, shipping_amount, tax_amount):
    try:
        total_amount = float(amount) + float(shipping_amount) + float(tax_amount)
    except Exception as e:
        print str(e), "Exception"
        total_amount = amount
    
    return total_amount
        
    
        