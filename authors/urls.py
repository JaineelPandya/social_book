# authors/urls.py
from django.urls import include, path

from .views import AuthorsAndSellersListView, AuthorDetailView

app_name = "authors"

urlpatterns = [
    path('', AuthorsAndSellersListView.as_view(), name='list'),
    path('author/<int:user_id>/', AuthorDetailView.as_view(), name='detail'),
    # API endpoint removed from URL patterns to avoid import-time side effects.
]
