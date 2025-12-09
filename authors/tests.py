# authors/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthorsAndSellersTests(TestCase):
    def test_public_visibility_filter(self):
        u1 = User.objects.create_user(username='a', email='a@example.com', password='pw')
        u2 = User.objects.create_user(username='b', email='b@example.com', password='pw')
        u1.profile.public_visibility = True
        u1.profile.save()
        u2.profile.public_visibility = False
        u2.profile.save()

        resp = self.client.get('/authors-sellers/')
        self.assertContains(resp, 'a')   # user a should be visible
        self.assertNotContains(resp, 'b')  # user b not visible
