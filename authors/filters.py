# authors/filters.py
import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class AuthorSellerFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='filter_q', label="Search")
    role = django_filters.ChoiceFilter(
        label="Role",
        choices=(
            ('all', 'All'),
            ('author', 'Author'),
            ('seller', 'Seller'),
            ('author_seller', 'Author & Seller'),
        ),
        method='filter_role',
        field_name='role'
    )

    class Meta:
        model = User
        fields = ['q', 'role']

    def filter_q(self, queryset, name, value):
        # search on email, first_name, last_name
        return queryset.filter(
            Q(email__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value)
        )

    def filter_role(self, queryset, name, value):
        # CustomUser doesn't have role fields, just return all users for now
        # Adapt this if you add is_author/is_seller fields to CustomUser
        return queryset
