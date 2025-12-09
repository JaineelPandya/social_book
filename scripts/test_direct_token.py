import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_book.settings')
django.setup()

from accounts.models import CustomUser
from rest_framework.authtoken.models import Token
from django.test import Client

user = CustomUser.objects.get(email='admin@example.com')
print('got user', user.email)

token_obj, created = Token.objects.get_or_create(user=user)
print('token created?', created)
print('TOKEN:', token_obj.key)

c = Client()
r = c.get('/api/my-files/', HTTP_AUTHORIZATION='Token ' + token_obj.key)
print('files_status', r.status_code)
print('content:', r.content.decode())
