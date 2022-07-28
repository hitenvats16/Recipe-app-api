# Test for Ingredient API

from decimal import Decimal

from core.models import Ingredient, Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import IngredientSerializer
from rest_framework import status
from rest_framework.test import APIClient

INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    # Create and return an Ingredient detail url
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='test@1234'):
    # Create and return User.
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsAPITest(TestCase):
    # Tests for aunthenticated API request
    def setUp(self) -> None:
        self.client = APIClient()

    def unauth_request_test(self):
        # Test for unauthenticated request
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    # Test for Authenticated Requests

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email='auth@example.com')
        self.client.force_authenticate(user=self.user)

    def test_retrive_list_of_ingredient(self):
        # Test for retrieving list of ingredient
        Ingredient.objects.create(name='salt', user=self.user)
        Ingredient.objects.create(name='pepper', user=self.user)

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_ingredient_limited_to_user(self):
        # Test for Ingredients limited to user
        user2 = create_user()
        Ingredient.objects.create(name='coriander', user=user2)
        ingredient = Ingredient.objects.create(name='samolina', user=self.user)

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        # Test for updating ingredient info

        ingredient = Ingredient.objects.create(user=self.user, name='Lettuse')

        payload = {
            'name': 'Chilly'
        }

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()

        self.assertEqual(res.data['name'], payload['name'])

    def test_delete_ingredient(self):
        # Test for deleting ingredient
        ingredient = Ingredient.objects.create(name='abc', user=self.user)

        url = detail_url(ingredient.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes"""
        ing1 = Ingredient.objects.create(user=self.user, name='apple')
        ing2 = Ingredient.objects.create(user=self.user, name='cider')
        recipe = Recipe.objects.create(
            title='Apple Cider Vineger',
            time_minutes=5,
            price=Decimal('4.5'),
            user=self.user,
        )
        recipe.ingredients.add(ing1)

        res = self.client.get(INGREDIENT_URL, {
            'assigned_only': 1
        })

        s1 = IngredientSerializer(ing1)
        s2 = IngredientSerializer(ing2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list"""
        ing = Ingredient.objects.create(
            name='ingredient',
            user=self.user
        )
        Ingredient.objects.create(
            user=self.user,
            name='Lent'
        )
        r1 = Recipe.objects.create(
            title='Recipe from heaven',
            price=Decimal('4.5'),
            user=self.user,
            time_minutes=34,
        )
        r2 = Recipe.objects.create(
            title='Recipe from hell',
            price=Decimal('4.5'),
            user=self.user,
            time_minutes=34,
        )
        r1.ingredients.add(ing)
        r2.ingredients.add(ing)

        res = self.client.get(INGREDIENT_URL, {
            'assigned_only': 1
        })

        self.assertEqual(len(res.data), 1)
