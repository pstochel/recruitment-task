from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers

from tasks.views import BookViewSet

router = routers.DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('books/<int:pk>/buy', BookViewSet.as_view({'post': 'buy'})),
]