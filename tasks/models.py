from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    """
    Account model holds current balance of every user.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    def change_balance(self, amount):
        operation = Operation.objects.create(balance_before=self.balance,
                                             amount=amount,
                                             account=self)

        self.balance += amount
        self.save()

class Operation(models.Model):
    """
    Each change (deposit, purchase, etc..) of Account's balance should be reflected
    in the Operation model for auditing purposes.
    """
    balance_before = models.DecimalField(decimal_places=2, max_digits=11)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


class Book(models.Model):
    """
    Model stores a title of the book and its price.
    """
    title = models.CharField(max_length=200)
    price = models.DecimalField(decimal_places=2, max_digits=10)

class Purchase(models.Model):
    """
    Model stores data about purchases.
    """
    dt_when = models.DateTimeField(default=timezone.now)
    books = models.ManyToManyField(Book)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


