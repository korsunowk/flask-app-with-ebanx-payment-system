from flask import Flask, render_template, \
    request, json, redirect, url_for, g

import requests
import binascii
import os
import sqlite3
import copy
import pprint

import settings

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(settings.DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def write_purchase_hash_to_db(purchase, hash_code):
    """
    Function for write new purchase hash code to database
    """
    cursor = get_db().cursor()
    # TODO change to UPDATE SET
    sql = "Insert INTO purchases (purchase_hash) VALUES ('%s')" % hash_code
    cursor.execute(sql)
    get_db().commit()


def write_purchase_to_db(data):
    """
    Function for write new purchase information to database
    :param data: all information about purchase
    """
    pass


@app.teardown_appcontext
def create_database_table(exception):
    """
    Create initial database table
    """
    table1 = """
        CREATE TABLE IF NOT EXISTS purchases (
             ID INTEGER PRIMARY KEY autoincrement,
             purchase_hash string
            );
    """
    table2 = """
        CREATE TABLE IF NOT EXISTS card_tokens (
            ID INTEGER PRIMARY KEY autoincrement,
            card_token string
        );
    """

    for sql in [table1, table2]:
        get_db().execute(sql)
        get_db().commit()


def write_card_token_to_db(token):
    """
    Function for write new token of card to database
    """
    # TODO change to UPDATE SET
    sql = "Insert INTO purchases (card_token) VALUES ('%s')" % token
    get_db().execute(sql)
    get_db().commit()


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

            reccuryng_body = {
                "integration_key": body['integration_key'],
                "payment_type_code": body['payment']['payment_type_code'],
                "creditcard": body['payment']['creditcard']
            }

            response = get_response_from_api(body=reccuryng_body,
                                             url=settings.EBANX_API_TOKEN_URL)

            if response['status'] == 'SUCCESS':
                new_body = copy.deepcopy(body)
                new_body['payment']['creditcard'] = response['token']

                # TODO write new_body to database
        else:
            body['payment'].update({
                "payment_type_code": data.get('pay-type'),
            })

        response = get_response_from_api(body=body,
                                         url=settings.EBANX_API_PAYMENT_URL)

        if response['status'] == 'SUCCESS':
            # TODO write_purchase_hash_to_db(response['payment']['hash'])
            context['purchase_hash'] = response['payment']['hash']

            return render_template('thanks_page.html', **context)

        context['error'] = response['status_message']

    return render_template('index.html', **context)


@app.route('/buy_one_more', methods=['POST'])
def buy_one_more():
    """
    Method for buy one more staff with card token instead full info
    """
    data = 'nothing'
    response = get_response_from_api(body=data,
                                     url=settings.EBANX_API_PAYMENT_URL)

    pprint.pprint(response)

    if response['status'] == 'SUCCESS':
        return render_template('thanks_page.html')

    return render_template('index.html')


def get_response_from_api(body, url):
    """
    Help function to send data to EBANX API and get response from one
    
    :param body: dictionary with data which needed to api
    :param url: url of api
    :return: response from EBANX api
    """
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


@app.route('/cancel/<purchase_hash>')
def cancel_payment(purchase_hash):
    """
    Cancel previous payment, if it possible
    """
    body = {
        'integration_key': settings.INTEGRATION_KEY,
        'hash': purchase_hash
    }

    response = get_response_from_api(body=body,
                                     url=settings.EBANX_API_CANCEL_URL)

    if response['status'] == 'SUCCESS':
        return redirect(url_for('cancelled_page'))

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
