import binascii
import requests
import json
import os
import unittest
import sys
from pathlib import Path


class BoletoTestCase(unittest.TestCase):
    """
        Test Case for boleto payment method
    """
    def setUp(self):
        """
        Set up initial values for tests
        """
        import task

        self.client = task.app.test_client()
        self.key = 'private key'
        self.url = 'https://sandbox.ebanx.com/ws/direct'

        self.body = {
            'integration_key': self.key,
            'operation': 'request',
            'payment': {
                "email": "some@email.com",
                "name": "José Silva",
                "country": "br",
                "document": "853.513.468-93",
                "zipcode": "61919-230",
                "address": "Rua E",
                "street_number": "1040",
                "city": "Maracanaú",
                "state": "CE",
                "phone_number": "8522847035",
                "birth_date": "12/04/1979",

                "merchant_payment_code": '',
                "currency_code": "BRL",
                'amount_total': '300',
                'payment_type_code': "boleto"
            }
        }

        self.view_body_boleto = {
            'email': 'email@email.com',
            'name': 'name',
            "country": 'br',
            "cpf": '853.513.468-93',
            "zip": "134134",
            "address": "address",
            "street-number": "134",
            "city": "Maracanaú",
            "state": "CE",
            "phone": "380980905082",
            "bdate": "12/04/1979",
            "currency": "BRL",
            "amount": "1",
            "pay-type": "boleto",
            "price": "300",
            "error-message": 'None'
        }

    def setNewMerchCode(self):
        """
        Help method for set new merchant payment code 
        (for payments needs only unique codes)
        """
        new_payment_code = binascii.hexlify(os.urandom(12)).decode('utf-8')
        self.body['payment']['merchant_payment_code'] = new_payment_code

    def testSuccessfulPayment(self):
        """
        Test simple successful payment 
        """
        self.setNewMerchCode()

        response = requests.post(self.url, json.dumps(self.body))

        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['status'], 'SUCCESS')

    def testWithoutMerchPayment(self):
        """
        Test payment without merchant_payment_code
        """
        response = requests.post(self.url, json.dumps(self.body))
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['status'], 'ERROR')

    def testIncorrectBDate(self):
        """
        Test with incorrect birth date
        """
        self.setNewMerchCode()
        self.body['payment']["birth_date"] = '21/21/2040'

        response = requests.post(self.url, json.dumps(self.body))
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['status'], 'ERROR')

    def testIncorrectDocument(self):
        """
        Test with incorrect document number
        """
        self.setNewMerchCode()
        self.body['payment']['document'] = 'document'

        response = requests.post(self.url, json.dumps(self.body))
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['status'], 'ERROR')

    def testIncorrectApiKey(self):
        """
        Test payment with incorrect api key
        """
        self.body['integration_key'] = 'incorrect_key'
        self.setNewMerchCode()

        response = requests.post(self.url, json.dumps(self.body))
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['status'], 'ERROR')

    def testGetIndexPage(self):
        """
        Test method for testing GET index page of application
        """
        content = self.client.get('/')
        self.assertEqual(content.status_code,  200)

    def testSuccessfulViewPayment(self):
        """
        Test successful payment with boleto
        """
        content = self.client.post('/', data=self.view_body_boleto)
        self.assertEqual(content.status_code, 200)

    def testSuccessfulViewCancelPayment(self):
        """
        Test successful cancel payment
        """
        content = self.client.post('/', data=self.view_body_boleto)
        content = content.data.decode('utf-8')
        href = content[
           content.find('/cancel/'):content.find('" data-type="cancel"')]
        content = self.client.get(href)
        self.assertTrue("cancelled" in content.data.decode('utf-8'))
        self.assertEqual(content.status_code, 302)


if __name__ == '__main__':
    top = Path(__file__).resolve().parents[1]
    sys.path.append(str(top))
    unittest.main()
