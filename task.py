from flask import Flask, render_template, \
    request, json, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

import requests
import binascii
import os

import settings

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] \
    = 'sqlite:////' + os.path.join(settings.PROJECT_DIR, settings.DATABASE)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Purchase(db.Model):
    """
    Simple model for purchase object
    """
    id = db.Column(db.Integer, primary_key=True)
    purchase_hash = db.Column(db.String(255), unique=True)
    card_token = db.Column(db.String(255))
    operation = db.Column(db.String(80))
    email = db.Column(db.String(80))
    name = db.Column(db.String(80))
    country = db.Column(db.String(80))
    document = db.Column(db.String(80))
    zipcode = db.Column(db.Integer)
    address = db.Column(db.String(80))
    street_number = db.Column(db.Integer)
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    phone_number = db.Column(db.Integer)
    birth_date = db.Column(db.String(80))
    currency_code = db.Column(db.String(80))
    amount_total = db.Column(db.Float)
    payment_type_code = db.Column(db.String(80))

    def __init__(self, operation, email, name,
                 country, document, zipcode, address, street_number, city,
                 state, phone_number, birth_date, currency_code,
                 amount_total, payment_type_code,
                 card_token='', purchase_hash=''):

        self.purchase_hash = purchase_hash
        self.card_token = card_token
        self.operation = operation
        self.email = email
        self.name = name
        self.country = country
        self.document = document
        self.zipcode = zipcode
        self.address = address
        self.street_number = street_number
        self.city = city
        self.state = state
        self.phone_number = phone_number
        self.birth_date = birth_date
        self.currency_code = currency_code
        self.amount_total = amount_total
        self.payment_type_code = payment_type_code

    def __str__(self):
        return "Purchase %d" % self.id

db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Index page of application with payment form
    """
    context = {}
    purchase = None

    if request.method == 'POST':
        data = request.form

        merchant_payment_code = generate_merchant_payment_code()
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

            reccuryng_body = {
                "integration_key": settings.INTEGRATION_KEY,
                "payment_type_code": data.get('card-type'),
                "creditcard": body['payment']['creditcard']
            }

            response = get_response_from_api(body=reccuryng_body,
                                             url=settings.EBANX_API_TOKEN_URL)

            if response['status'] == 'SUCCESS':
                purchase = Purchase(
                    card_token=response['token'],
                    operation=body['operation'],
                    email=body['payment']['email'],
                    name=body['payment']['name'],
                    country=body['payment']['country'],
                    document=body['payment']['document'],
                    zipcode=body['payment']['zipcode'],
                    address=body['payment']['address'],
                    street_number=body['payment']['street_number'],
                    city=body['payment']['city'],
                    state=body['payment']['state'],
                    phone_number=body['payment']['phone_number'],
                    birth_date=body['payment']['birth_date'],
                    currency_code=body['payment']['currency_code'],
                    amount_total=body['payment']['amount_total'],
                    payment_type_code=body['payment']['payment_type_code']
                )
                db.session.add(purchase)
                db.session.commit()

                context['card_payment'] = True
                context['amount'] = amount_total

        else:
            body['payment'].update({
                "payment_type_code": data.get('pay-type'),
            })
            purchase = Purchase(
                    operation=body['operation'],
                    email=body['payment']['email'],
                    name=body['payment']['name'],
                    country=body['payment']['country'],
                    document=body['payment']['document'],
                    zipcode=body['payment']['zipcode'],
                    address=body['payment']['address'],
                    street_number=body['payment']['street_number'],
                    city=body['payment']['city'],
                    state=body['payment']['state'],
                    phone_number=body['payment']['phone_number'],
                    birth_date=body['payment']['birth_date'],
                    currency_code=body['payment']['currency_code'],
                    amount_total=body['payment']['amount_total'],
                    payment_type_code=body['payment']['payment_type_code']
                )
            db.session.add(purchase)
            db.session.commit()

        response = get_response_from_api(body=body,
                                         url=settings.EBANX_API_PAYMENT_URL)

        if response['status'] == 'SUCCESS':
            purchase.purchase_hash = response['payment']['hash']
            db.session.add(purchase)
            db.session.commit()
            context['purchase_id'] = purchase.id

            return render_template('thanks_page.html', **context)

        context['error'] = response['status_message']

    return render_template('index.html', **context)


def generate_merchant_payment_code():
    """
    Generate random code for merchant payment
    :return: new random hash code
    """
    return binascii.hexlify(os.urandom(12)).decode('utf-8')


@app.route('/buy_one_more/<purchase_id>')
def buy_one_more(purchase_id):
    """
    Method for buy one more staff with card token instead full info

    :param purchase_id: INT id of purchase object in database
    """
    purchase = Purchase.query.get(purchase_id)

    body = {
        "integration_key": settings.INTEGRATION_KEY,
        "operation": purchase.operation,
        "mode": "full",
        "payment": {
            "merchant_payment_code": generate_merchant_payment_code(),
            "amount_total": purchase.amount_total,
            "currency_code": purchase.currency_code,
            "name": purchase.name,
            "email": purchase.email,
            "birth_date": purchase.birth_date,
            "document": purchase.document,
            "address": purchase.address,
            "street_number": purchase.street_number,
            "city": purchase.city,
            "state": purchase.state,
            "zipcode": purchase.zipcode,
            "country": purchase.country,
            "phone_number": purchase.phone_number,
            "payment_type_code": purchase.payment_type_code,
            "creditcard": {
                "token": purchase.card_token
            }
        }
    }
    response = get_response_from_api(body=body,
                                     url=settings.EBANX_API_PAYMENT_URL)

    if response['status'] == 'SUCCESS':
        new_purchase = Purchase(
            card_token=body['payment']['creditcard'].get('token'),
            operation=body['operation'],
            email=body['payment']['email'],
            name=body['payment']['name'],
            country=body['payment']['country'],
            document=body['payment']['document'],
            zipcode=body['payment']['zipcode'],
            address=body['payment']['address'],
            street_number=body['payment']['street_number'],
            city=body['payment']['city'],
            state=body['payment']['state'],
            phone_number=body['payment']['phone_number'],
            birth_date=body['payment']['birth_date'],
            currency_code=body['payment']['currency_code'],
            amount_total=body['payment']['amount_total'],
            payment_type_code=body['payment']['payment_type_code'],
            purchase_hash=response['payment']['hash']
        )
        db.session.add(new_purchase)
        db.session.commit()

        return render_template('thanks_page.html',
                               card_payment=True, second_payment=True,
                               purchase_id=new_purchase.id,
                               amount=new_purchase.amount_total)

    return redirect(url_for('index'))


def get_response_from_api(body, url, method='post'):
    """
    Help function to send data to EBANX API and get response from one
    
    :param body: dictionary with data which needed to api
    :param url: url of api
    :param method: HTTP method for request
    :return: response from EBANX api
    """
    if method == 'get':
        response = requests.get(url=url, params=body)
    else:
        response = requests.post(url=url,
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


@app.route('/cancelled')
def cancelled_page():
    """
    Simple page for display info of cancelled purchase
    """
    return render_template('cancelled_page.html')


@app.route('/refunded')
def refunded_page():
    """
    Simple page for display info of refunded purchase
    """
    return render_template('refunded_page.html')


@app.route('/cancel/<purchase_id>')
def cancel_payment(purchase_id):
    """
    Cancel previous payment, if it possible

    :param purchase_id: INT id of purchase object in database
    """
    purchase_hash = Purchase.query.get(purchase_id).purchase_hash

    body = {
        'integration_key': settings.INTEGRATION_KEY,
        'hash': purchase_hash
    }

    response = get_response_from_api(body=body,
                                     url=settings.EBANX_API_CANCEL_URL,
                                     method='get')

    if response['status'] == 'SUCCESS':
        return redirect(url_for('cancelled_page'))

    return redirect(url_for('index'))


@app.route('/refund/<purchase_id>', methods=['POST', 'GET'])
def refund_payment(purchase_id):
    """
    Function for refunds the sales order completely/partial
    :param purchase_id: INT id of purchase object in database
    """
    purchase_hash = Purchase.query.get(purchase_id).purchase_hash

    body = {
        'integration_key': settings.INTEGRATION_KEY,
        'operation': 'request',
        'hash': purchase_hash,
        'amount': Purchase.query.get(purchase_id).amount_total,
        'description': 'Refund payment on guitar'
    }

    if request.method == 'POST':
        body['amount'] = request.form.get('partial-refund')

    response = get_response_from_api(body=body,
                                     url=settings.EBANX_API_REFUND_URL,
                                     method='get')

    if response['status'] == 'SUCCESS':
        return redirect(url_for('refunded_page'))

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
