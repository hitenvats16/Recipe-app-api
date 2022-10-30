# Tests fro tags Api

from decimal import Decimal

from core.models import Tag, Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import TagsSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse('recipe:tag-list')


def create_user(email='user@example.com', password='Password@123'):
    # Create and return a test user
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(tag_url):
    return reverse('recipe:tag-detail', args=[tag_url])


class PublicTagsApiTest(TestCase):
    # Test unauthenticated API request

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        #  Test auth is required for retreiving tags.
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    # Test Authenticated API request

    def setUp(self):
        self.user = create_user(
            email='authenticated@example.com', password='Passworrd@1234')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retirive_tags(self):
        # Test retrieve a list of tags
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagsSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        # TEst list of tags is limited to authenticated user

        user2 = create_user()
        Tag.objects.create(user=user2, name='fruity')
        tag = Tag.objects.create(user=self.user, name='spice')

        res = self.client.get(TAGS_URL)
        res_data = res.data
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_data), 1)
        self.assertEqual(res_data[0]['name'], tag.name)
        self.assertEqual(res_data[0]['id'], tag.id)

    def test_update_tag(self):
        # Test updating a tag
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {
            'name': 'Dessert',
        }

        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tags(self):
        # Test for deleting tags from database
        tag = Tag.objects.create(user=self.user, name='Tag1')
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listings tag to those assigned to recipes."""

        tag1 = Tag.objects.create(user=self.user, name='breakfast')
        tag2 = Tag.objects.create(user=self.user, name='dinner')

        recipe = Recipe.objects.create(
            title='ANother recipe',
            time_minutes=4,
            price=Decimal('4.5'),
            user=self.user
        )

        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {
            'assigned_only': 1
        })

        s1 = TagsSerializer(tag1)
        s2 = TagsSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Dinner')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=5,
            price=Decimal('5.00'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=3,
            price=Decimal('2.00'),
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
