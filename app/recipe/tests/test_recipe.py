import os
import tempfile

from PIL import Image
from core.models import Recipe
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from rest_framework import status
from rest_framework.test import APIClient

from .test_utils import create_sample_user, sample_recipe, \
    create_sample_tag, create_sample_ingredient

from .common_tests import PublicAPIAccessTest

RECIPE_URL = reverse('recipe:recipe-list')


def get_recipe_details_url(recipe_id):
    """Returns Recipe details url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def get_recipe_image_upload_url(recipe_id):
    """Returns image upload url"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


class PublicRecipeApiTestCase(PublicAPIAccessTest, TestCase):
    """Test Ingredient Api public access"""
    endpoint = RECIPE_URL
    expected_status_code = status.HTTP_401_UNAUTHORIZED


class PrivateTapRecipeTestCases(TestCase):

    def setUp(self):
        self.user = create_sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_recipe_list_access(self):
        """Test authenticated user has access to recipe list"""
        sample_recipe(self.user)
        sample_recipe(self.user)
        recipes = Recipe.objects.all().order_by('-id')
        recipe_serializer = RecipeSerializer(recipes, many=True)
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, recipe_serializer.data)

    def test_recipe_limited_access(self):
        """
        Test Authenticated user has
        only limited access to recipe list
        """
        sample_recipe(self.user, title='new recipe')
        sample_recipe(create_sample_user(email="test1@example.com"))
        recipes = Recipe.objects.all().filter(user=self.user)
        recipe_serializer = RecipeSerializer(recipes, many=True)
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, recipe_serializer.data)

    def test_recipe_details(self):
        """Test Recipe detail with authenticated user"""
        recipe = sample_recipe(self.user)
        recipe.tags.add(create_sample_tag(self.user))
        recipe.ingredients.add(create_sample_ingredient(self.user))
        serializer = RecipeDetailSerializer(recipe)

        res = self.client.get(get_recipe_details_url(recipe.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_basic_create_recipe(self):
        """Test basic recipe creation """

        payload = {
            'title': 'sample recipe',
            'time_minutes': 10,
            'price': 5.00
        }

        res = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tag(self):
        tag1 = create_sample_tag(self.user, 'Vegan')
        tag2 = create_sample_tag(self.user, 'breakfast')
        payload = {
            'title': 'Maggie',
            'time_minutes': 5,
            'price': 10.00,
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(tags), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredient(self):
        ingredient1 = create_sample_ingredient(self.user, name='Maida')
        ingredient2 = create_sample_ingredient(self.user, name='Egg')
        payload = {
            'title': 'cake',
            'time_minutes': 30,
            'price': 20.00,
            'ingredients': [ingredient1.id, ingredient2.id]
        }

        res = self.client.post(RECIPE_URL, payload)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipes(self):
        """Test Recipe partial update"""
        recipe = sample_recipe(self.user)
        tag = create_sample_tag(self.user)
        recipe.tags.add(tag)
        updated_tag = create_sample_tag(self.user, name='NonVeg')
        payload = {
            'title': 'a new recipe',
            'time_minutes': 10,
            'price': 5.00,
            'tags': [updated_tag.id]
        }

        res = self.client.patch(get_recipe_details_url(recipe.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertIn(updated_tag, recipe.tags.all())

    def test_update_recipes(self):
        """Test Recipe update"""
        recipe = sample_recipe(self.user)
        tag = create_sample_tag(self.user)
        recipe.tags.add(tag)

        payload = {
            'title': 'a new recipe',
            'time_minutes': 11,
            'price': 15.00,
        }

        res = self.client.put(get_recipe_details_url(recipe.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.tags.count(), 0)


class RecipeImageUploadTestCases(TestCase):

    def setUp(self):
        self.user = create_sample_user()
        self.recipe = sample_recipe(self.user)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_image_upload(self):
        """Test successful image upload."""
        url = get_recipe_image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_invalid_image_upload(self):
        """Test invalid image upload."""
        url = get_recipe_image_upload_url(self.recipe.id)
        res = self.client.post(url,
                               {'image': 'invalid_image'},
                               format='multipart')
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipe_by_tag(self):
        """Test filter recipe with specific tag"""
        recipe = sample_recipe(self.user, title='Thai vegetable curry')
        recipe2 = sample_recipe(self.user, title='Mutton Curry')
        tag1 = create_sample_tag(self.user, name='Veg')
        tag2 = create_sample_tag(self.user, name='NonVeg')
        recipe.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_recipe(self.user, title='Dahi puri')

        res = self.client.get(RECIPE_URL, {'tags': f'{tag1.id},{tag2.id}'})

        serializer1 = RecipeSerializer(recipe)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipe_by_ingredients(self):
        """Test recipe filter by ingredients"""
        recipe = sample_recipe(self.user, title='Thai vegetable curry')
        recipe2 = sample_recipe(self.user, title='Mutton Curry')
        ingredient1 = create_sample_ingredient(self.user, 'tomato')
        ingredient2 = create_sample_ingredient(self.user, 'mutton')

        recipe.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        serializer1 = RecipeSerializer(recipe)
        serializer2 = RecipeSerializer(recipe2)

        res = self.client.get(RECIPE_URL, {'ingredients': f'{ingredient2.id}'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)
