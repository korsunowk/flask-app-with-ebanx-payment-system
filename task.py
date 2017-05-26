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
    sql = "UPDATE purchases SET purchase_hash='{0}' WHERE ID={1}"\
          .format(hash_code, purchase)
    cursor.execute(sql)
    get_db().commit()


def write_purchase_to_db(data):
    """
    Function for write new purchase information to database
    :param data: all information about purchase
    """
    payment = data.get('payment')
    cursor = get_db().cursor()
    sql = "INSERT INTO purchases (operation, email, name, " \
          "country, document, zipcode, address, street_number, " \
          "city, state, phone_number, birth_date, " \
          "currency_code, amount_total, payment_type_code)" \
          " VALUES ('{0}', '{1}', '{2}', '{3}'," \
          "'{4}', '{5}', '{6}', '{7}'," \
          "'{8}', '{9}', '{10}', '{11}'," \
          "'{12}', '{13}', '{14}')"\
        .format(
            data.get('operation'), payment.get('email'), payment.get('name'),
            payment.get('country'), payment.get('document'),
            payment.get('zipcode'), payment.get('address'),
            payment.get('street_number'), payment.get('city'),
            payment.get('state'), payment.get('phone_number'),
            payment.get('birth_date'), payment.get('currency_code'),
            payment.get('amount_total'), payment.get('payment_type_code')
        )
    cursor.execute(sql)

    return cursor.lastrowid


@app.teardown_appcontext
def create_database_table(exception):
    """
    Create initial database table for save info about purchases
    """
    sql = """
        CREATE TABLE IF NOT EXISTS purchases (
             ID INTEGER PRIMARY KEY autoincrement,
             purchase_hash string,
             card_token string,
             operation string,
             email string,
             name string,
             country string,
             document string,
             zipcode string,
             address string,
             street_number string,
             city string,
             state string,
             phone_number string,
             birth_date string,
             currency_code string,
             amount_total string,
             payment_type_code string
            );
    """

    get_db().execute(sql)
    get_db().commit()


def write_card_token_to_db(purchase_id, token):
    """
    Function for write new token of card to database
    """
    # TODO change to UPDATE SET
    sql = "UPDATE purchases SET card_token='%s' WHERE ID=%d" \
          % (token, purchase_id)
    get_db().execute(sql)
    get_db().commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Index page of application with payment form
    """
    context = {}
    purchase_id = None

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
                "integration_key": settings.INTEGRATION_KEY,
                "payment_type_code": data.get('card-type'),
                "creditcard": body['payment']['creditcard']
            }

            response = get_response_from_api(body=reccuryng_body,
                                             url=settings.EBANX_API_TOKEN_URL)

            if response['status'] == 'SUCCESS':
                purchase_id = write_purchase_to_db(body)
                write_card_token_to_db(purchase_id, response['token'])

        else:
            body['payment'].update({
                "payment_type_code": data.get('pay-type'),
            })
            purchase_id = write_purchase_to_db(body)

        response = get_response_from_api(body=body,
                                         url=settings.EBANX_API_PAYMENT_URL)

        if response['status'] == 'SUCCESS':
            write_purchase_hash_to_db(purchase=purchase_id,
                                      hash_code=response['payment']['hash'])
            context['purchase_id'] = purchase_id

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


def get_purchase_hash_from_db(purchase_id):
    cursor = get_db().cursor()
    sql = "SELECT purchase_hash FROM purchases WHERE ID=%s" % purchase_id
    cursor.execute(sql)
    return cursor.fetchone()


@app.route('/cancel/<purchase_id>')
def cancel_payment(purchase_id):
    """
    Cancel previous payment, if it possible
    """
    purchase_hash = get_purchase_hash_from_db(purchase_id)

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
