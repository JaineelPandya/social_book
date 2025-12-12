"""Token generator for email verification."""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Generate unique tokens for email verification."""
    
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.email_verified)
        )


account_activation_token = AccountActivationTokenGenerator()
