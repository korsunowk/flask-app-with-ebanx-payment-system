from flask import Flask, render_template, \
    request, json

import requests

import settings


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form

        body = {
            'integration_key': settings.INTEGRATION_KEY,
            'operation': 'request',
            'payment': dict()
        }
        print(data)
        if data.get('pay-type', False) == 'credit-card':
            body['payment'] = {
                'amount_total': '300',
                "currency_code": "BRL",
                "merchant_payment_code": "test_payment_code",
                "payment_type_code": data.get('card-type'),

                "email": "test@mail.ru",
                "name": "ehrr",
                "document": "853.513.468-93",
                "zipcode": "61919-230",
                "address": "eprogqerg",
                "street_number": "324",
                "city": "rewgr",
                "state": 'CE',
                "country": "BR",
                "phone_number": "8522847035",

                "creditcard": {
                    'card_number': data.get('card-number'),
                    'card_name': data.get('card-name'),
                    'card_due_date': '12/2019',
                    'card_cvv': data.get('card-cvv')
                }
            }
            response = requests.post(settings.EBANX_API_PAYMENT_URL,
                                     data=json.dumps(body))
            print(response.content)
        else:
            pass

    return render_template('index.html')


@app.route('/pay-type', methods=['GET'])
def pay_type():
    template = render_template('partials/card-info-block.html')

    if request.args.get('pay-type', False) == 'boleto':
        template = render_template('partials/boleto-info-block.html')

    response = app.response_class(
        response=json.dumps({
            'success': 'true',
            'template': template
        }),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
