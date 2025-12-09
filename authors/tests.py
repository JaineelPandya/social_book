# authors/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthorsAndSellersTests(TestCase):
    def test_public_visibility_filter(self):
        # Create users using email (CustomUser uses email as USERNAME_FIELD)
        u1 = User.objects.create_user(email='a@example.com', password='pw')
        u2 = User.objects.create_user(email='b@example.com', password='pw')
        # set visibility on user model
        u1.public_visibility = True
        u1.save()
        u2.public_visibility = False
        u2.save()

        resp = self.client.get('/authors-sellers/')
        # check presence by email
        self.assertContains(resp, 'a@example.com')   # user a should be visible
        self.assertNotContains(resp, 'b@example.com')  # user b not visible
