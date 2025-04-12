# accounts/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class BanUserTest(TestCase):
    def setUp(self):
        # Create an admin user
        self.admin = User.objects.create_user(username='admin', password='adminpass')
        self.admin.is_staff = True
        self.admin.save()

        # Create a regular user
        self.regular_user = User.objects.create_user(username='regular', password='regularpass')
        # Verify that the Profile has been created
        self.assertFalse(self.regular_user.profile.is_banned)

        self.client = Client()

    def test_banned_user_cannot_login(self):
        # First, simulate banning the user:
        self.regular_user.profile.is_banned = True
        self.regular_user.profile.save()

        # Attempt to login as the banned user:
        response = self.client.post(reverse('auths:login'), {
            'username': 'regular',
            'password': 'regularpass'
        })

        # Check that the response indicates a ban (assuming your template shows error message)
        self.assertContains(response, "banned", status_code=200)

    def test_unbanned_user_can_login(self):
        # Ensure the user is not banned:
        self.regular_user.profile.is_banned = False
        self.regular_user.profile.save()

        # Attempt login as the unbanned user:
        response = self.client.post(reverse('auths:login'), {
            'username': 'regular',
            'password': 'regularpass'
        })

        # The login should succeed, e.g., via a redirect:
        self.assertEqual(response.status_code, 302)
        # Optionally, check the destination URL:
        self.assertIn(reverse('landing:landing_page'), response.url)
