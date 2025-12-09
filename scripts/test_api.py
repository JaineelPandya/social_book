import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_book.settings')
django.setup()

from django.test import Client

c = Client()
try:
    r = c.post('/api/auth/token/login/', json.dumps({'email': 'admin@example.com', 'password': 'pass'}), content_type='application/json')
    print('status', r.status_code)
    print(r.content.decode())
    if r.status_code == 200:
        token = json.loads(r.content.decode()).get('auth_token')
        print('TOKEN:' + token)
        r2 = c.get('/api/my-files/', HTTP_AUTHORIZATION='Token ' + token)
        print('files_status', r2.status_code)
        print(r2.content.decode())
    else:
        print('login failed')
except Exception:
    import traceback
    traceback.print_exc()

    # Secondary test: create/get token directly and call the files API to verify permissions
    from accounts.models import CustomUser
    from rest_framework.authtoken.models import Token
    try:
        user = CustomUser.objects.get(email='admin@example.com')
        token_obj, _ = Token.objects.get_or_create(user=user)
        print('DIRECT_TOKEN:' + token_obj.key)
        r3 = c.get('/api/my-files/', HTTP_AUTHORIZATION='Token ' + token_obj.key)
        print('direct_files_status', r3.status_code)
        print(r3.content.decode())
    except Exception:
        import traceback
        traceback.print_exc()
