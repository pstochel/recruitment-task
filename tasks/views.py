from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tasks.models import Book, Account, Purchase, Operation
from tasks.serializers import BookSerializer


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """

    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer


    @action(
        detail=False,
        methods=['post'],
        url_path='buy',
        permission_classes=[IsAuthenticated]
    )
    def buy(self, request, pk=None):
        data = request.data
        books_ids = data.get('books', [])
        # assumption that we can buy only one piece of each book todo implement that case

        books = Book.objects.filter(id__in=books_ids)
        sum_price = sum(book.price for book in list(books))
        # books.aggregate(amount=Sum('price'))['price']

        user = request.user
        account = Account.objects.get(owner_id=user.id)

        current_account_balance = account.balance
        if sum_price > current_account_balance and sum_price > 0:
            return Response(data={"books": [], "amount": 0}, status=status.HTTP_406_NOT_ACCEPTABLE)

        purchase = Purchase.objects.create(books=books, account=account)
        account.change_balance(sum_price)

        operation = Operation.objects.create(balance_before=current_account_balance,
                                             balance_after=account.balance,
                                             account=-account)

        return Response(data={"books": books_ids, "amount": sum_price},
                        status=status.HTTP_200_OK)