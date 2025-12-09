# authors/views.py
from django.views.generic import ListView


class AuthorsAndSellersListView(ListView):
    """ListView for authors and sellers. Imports user model and filters lazily
    to avoid import-time side effects during project startup.
    """
    model = None
    template_name = "authors/authors_and_sellers.html"
    context_object_name = "users"
    paginate_by = 24  # adjust to taste

    def get_queryset(self):
        # Lazy imports to avoid import-time errors when Django loads URLconf
        from django.contrib.auth import get_user_model
        from .filters import AuthorSellerFilter

        User = get_user_model()

        qs = User.objects.select_related('profile').filter(
            profile__public_visibility=True,
            is_active=True
        ).order_by('-date_joined')  # or custom ordering

        # apply django-filter
        self.filterset = AuthorSellerFilter(self.request.GET, queryset=qs)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter'] = getattr(self, 'filterset', None)
        return ctx
