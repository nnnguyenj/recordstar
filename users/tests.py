from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile
from allauth.socialaccount.models import SocialApp
from unittest.mock import patch
from django.contrib.sites.models import Site
from django.contrib.auth import logout


class UserTests(TestCase):
    def setUp(self):
        site = Site.objects.create(domain='localhost', name='localhost')
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.profile = Profile.objects.create(user=self.user)

        social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='test-client-id',
            secret='test-secret'
        )
        social_app.sites.add(site)  # Link to site

    def test_user_login(self):
        # Test if the user can log in
        response = self.client.post(reverse('account_login'), {'login': 'testuser', 'password': 'password123'})
        self.assertRedirects(response, reverse('dashboard'))  # Change 'dashboard' to the correct redirect URL

    def test_user_logout(self):
        # Test user can log out
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('account_logout'), follow=True)

        # Expecting redirect to home ('/')
        self.assertRedirects(response, '/')

    def test_dashboard_view(self):
        # Test if logged in user can access dashboard
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_profile_view(self):
        # Test access to profile page for logged-in user
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')

    def test_upgrade_user_to_librarian(self):
        # Test if only librarians can upgrade other users
        # Create librarian user
        self.librarian = User.objects.create_user(username='librarian', password='password123')

        # Create profile for librarian
        self.librarian_profile = Profile.objects.create(user=self.librarian)
        self.librarian_profile.account_type = 'L'
        self.librarian_profile.save()

        self.client.login(username='librarian', password='password123')
        response = self.client.post(reverse('upgrade_user', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User successfully upgraded to librarian')

    def test_forbidden_upgrade(self):
        # Test if non-librarians can't upgrade other users
        self.client.login(username="testuser", password="password123")  # Fix password
        response = self.client.post(reverse('upgrade_user', args=[self.user.id]))
        self.assertEqual(response.status_code, 403)
