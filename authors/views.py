# authors/views.py
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


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

        qs = User.objects.filter(
            public_visibility=True,
            is_active=True
        ).order_by('-date_joined')  # or custom ordering

        # apply django-filter
        self.filterset = AuthorSellerFilter(self.request.GET, queryset=qs)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter'] = getattr(self, 'filterset', None)
        return ctx


class AuthorDetailView(DetailView):
    """Detail view for a single author showing their public books."""
    model = None
    template_name = "authors/author_detail.html"
    context_object_name = "author"
    pk_url_kwarg = "user_id"
    
    def get_queryset(self):
        """Get user queryset."""
        return User.objects.filter(public_visibility=True, is_active=True)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Get author's public books
        from accounts.models import UploadedFile
        books = UploadedFile.objects.filter(
            user=self.object,
            visibility='public',
            is_active=True
        ).order_by('-uploaded_at')
        ctx['books'] = books
        ctx['books_count'] = books.count()
        return ctx
