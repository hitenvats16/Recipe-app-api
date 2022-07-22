from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    # Create and return a new User
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    # Test the public features of the user API

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        # Test creating a user is successfull
        payload = {
            'email': 'ltes@example.com',
            'password': 'Password@123',
            'name': 'Test User'
        }

        res = APIClient().post(path=CREATE_USER_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertNotContains('password', res)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

    def test_user_exist_with_email_exists(self):
        # Test for user exist with email exist
        payload = {
            'email': 'ltes@example.com',
            'password': 'Password@123',
            'name': 'Test User'
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        # Test an error is return if pass is less than 5 characters
        payload = {
            'email': 'ltes@example.com',
            'password': 'Pas',
            'name': 'Test User'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload['email']).exist()
        self.assertFalse(user_exist)
