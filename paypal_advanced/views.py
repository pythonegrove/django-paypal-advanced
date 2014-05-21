#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pycurl
import cStringIO
import uuid

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from paypal_advanced.models import *
from paypal_advanced.utils import *


def home(request):
    '''
    Renders Checkout Form
    '''
    checkout_form = CheckoutForm()

    try:
        if request.method == "POST":
            checkout_form = CheckoutForm(request.POST)
            if checkout_form.is_valid():
                checkout = checkout_form.save(commit=False)
                checkout.status = "In Process"
                checkout.save()

                iframe_variables = {}
                amount = float(checkout.total)
                ship_amount = float(checkout.shipping_cost)
                tax = float(checkout.tax)
                ship_firstname = str(checkout.first_name)
                ship_lastname = str(checkout.last_name)
                ship_city = str(checkout.ship_city)
                ship_street = str(checkout.ship_street)
                ship_state = str(checkout.ship_state)
                ship_zipcode = str(checkout.ship_postal_code)
                ship_country = str(checkout.ship_country)
                phone = str(checkout.phone)
                email = str(checkout.email)
                invoice_number = str(checkout.invoice_number)
                po_number = str(checkout.id)

                token = create_secure_token(amount=amount, ship_amount=ship_amount, tax=tax, ship_firstname=ship_firstname, ship_lastname=ship_lastname,
                                            ship_city=ship_city, ship_street=ship_street, ship_state=ship_state, ship_zipcode=ship_zipcode,
                                            ship_country=ship_country, phone=phone, email=email, invoice_number=invoice_number, po_number=po_number)

                iframe_variables['token'] = token

                try:

                    iframe_settings = IframeSettings.objects.all()[0]
                    if iframe_settings:
                        iframe_variables['iframe_width'] = iframe_settings.width
                        iframe_variables['iframe_height'] = iframe_settings.height
                        iframe_variables['iframe_scrolling'] = iframe_settings.scrolling

                except IndexError:
                    iframe_variables['iframe_width'] = "570"
                    iframe_variables['iframe_height'] = "540"
                    iframe_variables['iframe_scrolling'] = "No"

                except:
                    pass
                
                return render_to_response(    
                    'payment_home.html',
                    iframe_variables,
                    context_instance = RequestContext(request),
                )
            else:
                checkout_form =  CheckoutForm(request.POST)
    except:
        pass
    
    return render_to_response(
                'payment_index.html',
                {'checkout_form':checkout_form},
                context_instance = RequestContext(request),
            )


def create_secure_token(amount, ship_amount=0, tax=0, ship_firstname=None, ship_lastname=None,
                        ship_city=None, ship_street=None, ship_state=None, ship_zipcode=None,
                        ship_country=None, phone=None, email=None, invoice_number=1, po_number=2):
    """
    Create the secure token and secure token id
    """

    response = cStringIO.StringIO()
    c = pycurl.Curl()
    token_id = uuid.uuid4()

    try:

        merchant_settings = MerchantAccountSettings.objects.all()[0]
        if merchant_settings:
            partner = str(merchant_settings.partner)
            vendor = str(merchant_settings.vendor)
            paypal_user = str(merchant_settings.paypal_user)
            paypal_password = str(merchant_settings.paypal_password)
            currency_code = str(merchant_settings.currency.currency_code)

    except IndexError:
        partner = "PayPal"
        vendor = "muthuvelegrove"
        paypal_user = "muthuvelegrove"
        paypal_password = "egrove@123"
        currency_code = 'USD'

    except:
        pass

    #print  'PARTNER=%s&VENDOR=%s&USER=%s&PWD=%s&TRXTYPE=%s&AMT=%s&CREATESECURETOKEN=%s&SECURETOKENID=%s' %(partner,vendor,paypal_user,paypal_password,'S',float(amount),'Y',token_id)

    try:
        mode = 'TEST'
        trans_mode = TransactionProcessMode.objects.all()[0]
        if trans_mode.mode == "Sandbox":
            URL = trans_mode.URL
        elif trans_mode.mode == "Live":
            URL = trans_mode.URL
            mode = 'LIVE'
        else:
            URL = 'https://pilot-payflowpro.paypal.com'
    except IndexError:
        URL = 'https://pilot-payflowpro.paypal.com'

    except:
        pass

    total_amount = calculate_total_amount(amount, ship_amount, tax)
    c.setopt(c.URL, str(URL))

    c.setopt(c.POSTFIELDS,
                'PONUM=%s&INVNUM=%s&PARTNER=%s&VENDOR=%s&USER=%s&PWD=%s&TRXTYPE=%s&AMT=%s&CREATESECURETOKEN=%s&SECURETOKENID=%s&CURRENCY=%s&SHIPAMOUNT=%s&TAX=%s&SHIPTOFIRSTNAME=%s&SHIPTOLASTNAME=%s&SHIPTOSTREET=%s&SHIPTOCITY=%s&SHIPTOSTATE=%s&SHIPTOCOUNTRY=%s&SHIPTOZIP=%s&SHIPTOPHONE=%s&SHIPTOEMAIL=%s' %(po_number, invoice_number, partner,
                vendor,
                paypal_user,
                paypal_password,
                'S',
                float(total_amount),
                'Y',
                token_id,
                currency_code,
                ship_amount,
                tax,
                ship_firstname,
                ship_lastname,
                ship_street,
                ship_city,
                ship_state,
                ship_country,
                ship_zipcode,
                phone,
                email
                )
            )

    #c.setopt(c.POSTFIELDS,'PARTNER=%s&VENDOR=%s&USER=%s&PWD=%s&TRXTYPE=%s&AMT=%s&CREATESECURETOKEN=%s&SECURETOKENID=%s' %("PayPal", "muthuvelegrove", "muthuvelegrove", 'egrove@123', 'S', '40.00', 'Y', '92528208de1413abc3d60c86cb15') )
    c.setopt(c.WRITEFUNCTION, response.write)
    c.perform()
    c.close()
    result = response.getvalue().split('&')[0].split('=')[1]
    secure_token = ''
    secure_token_id = ''
    if int(result) == 0:
        secure_token = response.getvalue().split('&')[1].split('=')[1]
        secure_token_id = response.getvalue().split('&')[2].split('=')[1]
    elif int(result) == 1:
        secure_token_id = response.getvalue().split('&')[1].split('=')[1]
    else:
        pass

    return {
        'secure_token': secure_token,
        'secure_token_id': secure_token_id,
        'mode': mode
        }


@csrf_exempt
def payment_success(request):
    """
    Process the paypal payment success response.

    PAYPAL RESPONSE:
    {
    u'TAX': [u'1.00'], u'SHIPTOSTREET': [u'134 Cannongate III'],
    u'BILLTOEMAIL': [u'egroveqa1@gmail.com'], u'LASTNAME': [u'eGrove'],
    u'SHIPTOCITY': [u'Nashua'], u'AVSDATA': [u'YYY'], u'TENDER': [u'P'],
    u'EMAIL': [u'egroveqa1@gmail.com'], u'CORRELATIONID': [u'bf563f0be7930'],
    u'SECURETOKEN': [u'7s6eaDHdMOEK9Ik6q6BGZ0AXd'], u'PENDINGREASON': [u'unilateral'],
    u'TAXAMT': [u'1.00'], u'BILLTONAME': [u'Secret eGrove'], u'BILLTOFIRSTNAME': [u'Secret'],
    u'AVSZIP': [u'Y'], u'EMAILTOSHIP': [u'selvas@egrovesystems.com'], u'INVOICE': [u'1'],
    u'COUNTRY': [u'US'], u'COUNTRYTOSHIP': [u'US'], u'AMT': [u'13.00'], u'RESULT': [u'0'],
    u'PAYERID': [u'XY2PJKAPKWNSS'], u'NAMETOSHIP': [u'Selva Kumar'], u'SHIPTOCOUNTRY': [u'US'],
    u'ZIPTOSHIP': [u'03063'], u'ADDRESSTOSHIP': [u'134 Cannongate III'], u'PAYMENTTYPE': [u'instant'],
    u'TOKEN': [u'EC-86A07502JL503744R'], u'INVNUM': [u'1'], u'SHIPTOZIP': [u'03063'],
    u'AVSADDR': [u'Y'], u'TRANSTIME': [u'2013-05-23 06:16:15'], u'STATETOSHIP': [u'NH'],
    u'BILLTOLASTNAME': [u'eGrove'], u'NAME': [u'Secret eGrove'], u'FIRSTNAME': [u'Secret'],
    u'CITYTOSHIP': [u'Nashua'], u'SHIPTOSTATE': [u'NH'], u'PONUM': [u'2'], u'METHOD': [u'P'],
    u'RESPMSG': [u'Approved'], u'PNREF': [u'E18P4D2A1786'], u'BILLTOCOUNTRY': [u'US'],
    u'PPREF': [u'9E374076UF1550948'], u'TYPE': [u'S'],
    u'SECURETOKENID': [u'3d46c341-8948-4a17-b58c-a24e3777e24f']
    }

    Card Payment
    {
    u'AVSDATA': [u'XXN'], u'COUNTRY': [u'US'], u'SHIPTOCITY': [u'Nashua'],
    u'EXPDATE': [u'0518'], u'HOSTCODE': [u'10002'], u'TENDER': [u'CC'],
    u'ACCT': [u'0340'], u'SECURETOKEN': [u'78XFa8zzcCEiR11BWjh3A4w7o'],
    u'SHIPTOSTREET': [u'134 Cannongate III'], u'CARDTYPE': [u'0'], u'TAX': [u'1.00'],
    u'EMAILTOSHIP': [u'selvas@egrovesystems.com'], u'NAMETOSHIP': [u'Selva Kumar'],
    u'LASTNAME': [u'NotProvided'], u'COUNTRYTOSHIP': [u'US'], u'AMT': [u'13.00'],
    u'RESULT': [u'5'], u'INVOICE': [u'1'], u'SHIPTOCOUNTRY': [u'US'], u'ZIPTOSHIP': [u'03063'],
    u'ADDRESSTOSHIP': [u'134 Cannongate III'], u'INVNUM': [u'1'], u'SHIPTOZIP': [u'03063'],
    u'TRANSTIME': [u'2013-05-23 06:22:10'], u'STATETOSHIP': [u'NH'], u'CITYTOSHIP': [u'Nashua'],
    u'SHIPTOSTATE': [u'NH'], u'PONUM': [u'2'], u'METHOD': [u'CC'],
    u'RESPMSG': [u'Invalid merchant information: 10002-Account is not verified'],
    u'PNREF': [u'E19P4D2A2386'], u'BILLTOCOUNTRY': [u'US'], u'TYPE': [u'S'],
    u'SECURETOKENID': [u'53b9560e-512d-4cab-b06a-393f84f2589a']
    }


    """

    response_msg = {}
    msg = ''

    try:
        response = request.POST
        if response:
            transaction_status = TransactionStatus.objects.create(
                order_id=response['PONUM'],
                invoice_number = response['INVNUM'],
                transaction_id = response['PNREF'],
                amount = response['AMT'],
                timestamp = response['TRANSTIME'],
                status = response['RESPMSG'],
                )
            transaction_status.save()
            #response['METHOD'] == "P": #User pay amount via paypal
            #response['METHOD'] == "CC": #User pay amount via CreditCard

        if response['PONUM']:
            checkout_detail = CheckOutDetails.objects.get(id=response['PONUM'])
            checkout_detail.status = "Complete"
            checkout_detail.save()

        msg = str(response['RESPMSG'])
        response_msg['pnrref'] = response['PNREF']
        response_msg['amount'] = response['AMT']

    except:
        if request.method == "GET":
            response = request.GET
            if response and response['cancel_ec_trans'] == 'true':
                msg = "Transaction Cancelled"
            else:
                msg = "Payment not received. Error in your payment"
        if request.method == "POST":
            response = request.POST
            msg = str(response['RESPMSG'])

    response_msg['message'] = msg

    return render_to_response('response.html',
                              response_msg,
                              context_instance = RequestContext(request),
                              )
