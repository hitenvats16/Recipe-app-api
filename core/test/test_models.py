# Test for models

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from decimal import Decimal
from unittest.mock import patch


def create_user(email='user@example.com', password='Password@123'):
    # Create a new test user
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTest(TestCase):
    # Test models

    def test_create_user_with_email_successful(self):
        # Test creating a user with an email is successful
        _email = 'test@example.com'
        _password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=_email,
            password=_password
        )
        self.assertEqual(user.email, _email)
        self.assertTrue(user.check_password(_password))

    def test_new_user_email_normalized(self):
        # Test email is normalized for new users.
        sample_emails = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com'],
        ]

        for _email, expected in sample_emails:
            user = get_user_model().objects.create_user(_email, 'Password@123')
            self.assertEqual(user.email, expected)

    def new_user_without_email_raises_error(self):
        # Test that creating a user without an email raises a ValueError.
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='Password@123'
            )

    def test_create_superuser(self):
        # Test creating a superuser
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'Password@123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_recipe(self):
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='password@123'
        )

        recipe = models.Recipe.objects.create(
            title='Recipe',
            price=5,
            user=user,
            time_minutes=Decimal('5.5'),
            description='Sample discription for the recipe'
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        # Test creating a tag is successfull
        user = create_user()
        tag = models.Tag(user=user, name='tag1')
        self.assertEqual(tag.name, str(tag))

    def test_create_ingredient(self):
        # Test creatinf an ingredient
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            name='Ingredient1',
            user=user
        )
        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
