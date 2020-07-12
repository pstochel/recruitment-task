import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from rest_framework import status

from tasks.models import Book, Account


class ViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345')
        self.user.save()
        self.client.login(username='testuser', password='12345')

    def test_buy(self):
        acc, _ = Account.objects.get_or_create(owner=self.user)

        # Empty account
        b1, _ = Book.objects.get_or_create(title="The Little Prince", price=10.45)
        b2, _ = Book.objects.get_or_create(title="Winnie the Pooh", price=34.99)

        resp = self.client.post('/books/buy/',
                                data=json.dumps({"books": [b1.id, b2.id]}),
                                content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(resp.content), ['No books selected to buy.'])
        self.assertEqual(acc.purchase_set.count(), 0)
        self.assertEqual(acc.balance, 0)

        initial_balance = 100
        acc.change_balance(initial_balance)

        # No books chosen
        resp = self.client.post('/books/buy/',
                                data=json.dumps({"books": []}),
                                content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(resp.content), {"books": [], "amount": 0})
        self.assertEqual(acc.purchase_set.count(), 0)
        self.assertEqual(acc.balance, initial_balance)

        # Books chosen

        resp = self.client.post('/books/buy/',
                                data=json.dumps({"books": [b1.id, b2.id]}),
                                content_type='application/json')
        acc.refresh_from_db()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(resp.content), {"books": [b1.id, b2.id], "amount": 45.44})
        self.assertEqual(acc.purchase_set.count(), 1)
        self.assertAlmostEqual(acc.balance, Decimal('54.56'))

