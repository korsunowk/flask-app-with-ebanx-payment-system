from flask import Flask, render_template, \
    request, json, redirect, url_for

import requests
import binascii
import os

import settings

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Index page of application with payment form
    """
    context = {}

    if request.method == 'POST':
        data = request.form

        # random staff code
        merchant_payment_code \
            = binascii.hexlify(os.urandom(12)).decode('utf-8')
        amount_total = int(data.get('price')) * int(data.get('amount'))
        body = {
            'integration_key': settings.INTEGRATION_KEY,
            'operation': 'request',
            'payment': {
                "email": data.get('email'),
                "name": data.get('name'),
                "country": data.get('country'),
                "document": data.get('cpf'),
                "zipcode": data.get('zip'),
                "address": data.get('address'),
                "street_number": data.get('street-number'),
                "city": data.get('city'),
                "state": data.get('state'),
                "phone_number": data.get('phone'),
                "birth_date": data.get('bdate'),

                "merchant_payment_code": merchant_payment_code,
                "currency_code": data.get('currency'),
                'amount_total': amount_total,
            }
        }
        if data.get('pay-type') == 'credit-card':
            body['payment'].update({
                "payment_type_code": data.get('card-type'),
                "creditcard": {
                    'card_number': data.get('card-number'),
                    'card_name': data.get('card-name'),
                    'card_due_date': data.get('card-date'),
                    'card_cvv': data.get('card-cvv')
                }
            })
        else:
            body['payment'].update({
                "payment_type_code": data.get('pay-type'),
            })

        response = get_response_from_api(body)

        if response['status'] == 'SUCCESS':
            return redirect(url_for('thanks_page'))

        context['error'] = response['status_message']

    return render_template('index.html', **context)


def get_response_from_api(body):
    """
    Help function to send data to EBANX API and get response from one
    
    :param body: dictionary with data which needed to api 
    :return: response from EBANX api
    """
    response = requests.post(settings.EBANX_API_PAYMENT_URL,
                             data=json.dumps(body))
    response = json.loads(response.content.decode('utf-8'))
    return response


@app.route('/pay-type', methods=['GET'])
def pay_type():
    """
    Send partial html with card information to index page for user
    """
    response = app.response_class(
        response=json.dumps({
            'success': 'true',
            'template': render_template('partials/card-info-block.html')
        }),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route('/thanks')
def thanks_page():
    """
    Simple 'Thanks you' page for successful payments
    """
    return render_template('thanks_page.html')


if __name__ == '__main__':
    app.run()
