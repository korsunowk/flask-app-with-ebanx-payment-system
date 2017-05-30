import unittest
import os
import binascii
import requests
import json


class BoletoTestCase(unittest.TestCase):
    """
        Test Case for boleto payment method
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
                'payment_type_code': "boleto"
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


if __name__ == '__main__':
    unittest.main()
