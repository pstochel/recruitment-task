from django.db import transaction
from django.db.models import Sum
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tasks.models import Book, Account, Purchase
from tasks.serializers import BookSerializer

class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """

    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @transaction.atomic
    @action(
        detail=False,
        methods=['post'],
        url_path='buy',
        permission_classes=[IsAuthenticated]
    )
    def buy(self, request):
        data = request.data
        books_ids = data.get('books', [])

        # I assumed that uds are unique(user cannot buy two same books. I would consider sending extra information
        # about the quantity of the books.

        books = Book.objects.filter(id__in=books_ids)
        if books.count() == 0:
            raise serializers.ValidationError("No books selected to buy.")

        sum_price = books.aggregate(amount=Sum('price'))['amount'] or 0

        try:
            user = request.user
            account = Account.objects.select_for_update().get(owner_id=user.id)
        except Account.DoesNotExist:
            raise NotFound('An account for this username was not found.')

        current_account_balance = account.balance
        # check if there is enough money to buy books
        if sum_price > current_account_balance and sum_price > 0:
            return Response(data={"books": [], "amount": 0}, status=status.HTTP_406_NOT_ACCEPTABLE)

        purchase = Purchase.objects.create(account=account)
        for book in books:
            purchase.books.add(book)
        purchase.save()

        account.change_balance(-sum_price)

        return Response(data={"books": books_ids, "amount": sum_price},
                        status=status.HTTP_200_OK)
