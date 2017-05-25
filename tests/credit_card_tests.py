import unittest
import os
import binascii
import requests
import json


class CreditCardTestCase(unittest.TestCase):
    """
        Test Case for payments with credit card
    """
    def setUp(self):
        """
        Set up initial values for tests
        """

        self.key = 'test_ik_lTp-YAT16nvn74DXKFFoYw'
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
                "payment_type_code": "visa",
                "creditcard": {
                        'card_number': "4242424242424242",
                        'card_name': "Card Name",
                        'card_due_date': "12/2019",
                        'card_cvv': "123"
                    }
                }
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
        Simple test successful payment
        """
        self.setNewMerchCode()
        response = requests.post(self.url, json.dumps(self.body))
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['status'], 'SUCCESS')

    def testUnsuccessfulPayment(self):
        """
        Simple test for unsuccessful payment without merchant payment
        """
        response = requests.post(self.url, json.dumps(self.body))
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['status'], 'ERROR')

    def testIncorrectCardNumber(self):
        """
        Test incorrect card number
        """
        self.setNewMerchCode()
        self.body['payment']['creditcard']['card_number'] = '0000'
        response = requests.post(self.url, json.dumps(self.body))
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['status'], 'ERROR')

    def testIncorrectCardCVV(self):
        """
        Test incorrect card CVV
        """
        self.setNewMerchCode()
        self.body['payment']['creditcard']['card_cvv'] = 'ABC'
        response = requests.post(self.url, json.dumps(self.body))
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['status'], 'ERROR')

    def testIncorrectCardDueDate(self):
        """
        Test incorrect card due date
        """
        self.setNewMerchCode()
        self.body['payment']['creditcard']['card_due_date'] = '22/2020'
        response = requests.post(self.url, json.dumps(self.body))
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['status'], 'ERROR')

    def testIncorrectCardType(self):
        """
        Test incorrect card type
        """
        self.setNewMerchCode()
        self.body['payment']['payment_type_code'] = 'Incorrect visa'
        response = requests.post(self.url, json.dumps(self.body))
        response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response['status'], 'ERROR')


if __name__ == '__main__':
    unittest.main()
