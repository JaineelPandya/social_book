from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # CustomUser uses email as the identifier (no username field)
        fields = ["id", "email", "first_name", "last_name", "is_active", "public_visibility"]