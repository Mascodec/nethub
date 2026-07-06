from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import authenticate

from .models import User


class PasswordResetAndAdminNavTests(TestCase):
    def test_password_reset_page_is_available(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_admin_nav_link_appears_for_admin_users(self):
        user = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='secret123',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Admin')

    def test_authentication_accepts_email_for_admin_users(self):
        user = User.objects.create_user(
            username='admin',
            email='admin@nethub.com',
            password='secret123',
            role='admin',
            is_staff=True,
            is_superuser=True,
        )

        authenticated = authenticate(username='admin@nethub.com', password='secret123')

        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated.id, user.id)
