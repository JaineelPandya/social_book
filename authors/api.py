from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import UserListSerializer   

User = get_user_model()


class AuthorsSellersListAPI(generics.ListAPIView):
    serializer_class = UserListSerializer

    def get_queryset(self):
        # CustomUser stores visibility on the user model (no related profile)
        return User.objects.filter(
            public_visibility=True,
            is_active=True
        ).order_by('-date_joined')
