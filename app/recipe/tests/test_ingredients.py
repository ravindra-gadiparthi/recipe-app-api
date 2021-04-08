from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import IngredientSerializer
from core.models import Ingredient
from .test_utils import create_sample_user, create_sample_ingredient, \
    sample_recipe

from .common_tests import PublicAPIAccessTest

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiAccessDeniedTests(PublicAPIAccessTest, TestCase):
    """Test Ingredient Api public access"""
    endpoint = INGREDIENT_URL
    expected_status_code = status.HTTP_401_UNAUTHORIZED


class PrivateIngredientTestCases(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_sample_user()
        self.client.force_authenticate(self.user)

    def test_ingredients_list_with_authenticated_user(self):
        """Test authenticated user can list ingredients"""
        Ingredient.objects.create(name='tomato', user=self.user)
        Ingredient.objects.create(name='tomato1', user=self.user)
        ingredients = Ingredient.objects.all().order_by('-name')
        ingredient_serializer = IngredientSerializer(ingredients, many=True)

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ingredient_serializer.data)

    def test_ingredients_access_with_authenticated_user(self):
        """Test authenticated user can only view ingredients create by him"""
        Ingredient.objects.create(name='tomato1',
                                  user=create_sample_user(
                                      email='test2@gmail.com'
                                  ))
        ingredient = Ingredient.objects.create(name='tomato', user=self.user)
        Ingredient.objects.all().order_by('-name')

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data))
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_authenticated_user_create_ingredient(self):
        """Test authenticated user can create Ingredient"""

        payload = {'name': 'tomato'}
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], payload['name'])

    def test_ingredient_create_with_invalid_name(self):
        """
        Test validation error when user tried to
        create invalid ingredient
        """
        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ingredient_filter_with_assigned_only(self):
        """
            Test Ingredient filtering with assigned only ingredients
        """
        recipe = sample_recipe(self.user, title='Cheese Cake')
        ingredient = create_sample_ingredient(self.user, name='Cheese')
        create_sample_ingredient(self.user, name='Ghee')
        recipe.ingredients.add(ingredient)
        serializer = IngredientSerializer(ingredient)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data)
        self.assertEqual(len(res.data), 1)

    def test_ingredient_filter_with_assigned_only_unique(self):
        """
        Test Ingredient filtering with assigned only ingredients
        returns unique ingredients
        """
        recipe1 = sample_recipe(self.user, title='Cheese Cake')
        recipe2 = sample_recipe(self.user, title='Cheese Maggie')
        ingredient = create_sample_ingredient(self.user, name='Cheese')
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)
        serializer = IngredientSerializer(ingredient)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data)
        self.assertEqual(len(res.data), 1)
