from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import UserListSerializer   

User = get_user_model()


class AuthorsSellersListAPI(generics.ListAPIView):
    serializer_class = UserListSerializer

    def get_queryset(self):
        return User.objects.select_related('profile').filter(
            profile__public_visibility=True,   
            is_active=True
        )
