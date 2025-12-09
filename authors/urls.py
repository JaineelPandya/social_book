# authors/urls.py
from django.urls import include, path

from .views import AuthorsAndSellersListView

app_name = "authors"

urlpatterns = [
    path('', AuthorsAndSellersListView.as_view(), name='list'),
    # API endpoint removed from URL patterns to avoid import-time side effects.
]
