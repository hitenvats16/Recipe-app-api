# Tests fro tags Api

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import TagsSerializer

from core.models import Tag

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
