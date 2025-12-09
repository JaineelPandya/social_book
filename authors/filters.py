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
        # search on username, first_name, last_name, email
        return queryset.filter(
            Q(username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value)
        )

    def filter_role(self, queryset, name, value):
        # assumes roles exist on related profile; adapt if fields are on User
        if value == 'author':
            return queryset.filter(profile__is_author=True)
        if value == 'seller':
            return queryset.filter(profile__is_seller=True)
        if value == 'author_seller':
            return queryset.filter(profile__is_author=True, profile__is_seller=True)
        return queryset
