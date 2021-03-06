from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from ..serializers import TagSerializer
from .test_utils import create_sample_user, create_sample_tag, \
    sample_recipe

from .common_tests import PublicAPIAccessTest

LIST_TAG_URL = reverse('recipe:tag-list')


class PublicApiTestCase(PublicAPIAccessTest, TestCase):
    endpoint = LIST_TAG_URL
    expected_status_code = status.HTTP_401_UNAUTHORIZED


class PrivateTapApiTestCases(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_sample_user()
        self.client.force_authenticate(self.user)

    def test_list_tags_with_authentication(self):
        """Test authenticated uses can query tags"""

        Tag.objects.create(user=self.user, name="tag1")
        Tag.objects.create(user=self.user, name="tag2")
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        res = self.client.get(LIST_TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_authenticated_users_queries(self):
        user1 = create_sample_user(email='test1@gmail.com')
        Tag.objects.create(user=user1, name='tag1')
        tag = Tag.objects.create(user=self.user, name='tag2')

        res = self.client.get(LIST_TAG_URL)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_authenticated_user_create_tags(self):
        payload = {'name': 'Tag1'}
        res = self.client.post(LIST_TAG_URL, payload)
        exists = Tag.objects.filter(user=self.user,
                                    name=payload['name']).exists()

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)
        self.assertEquals(res.data['name'], payload['name'])

    def test_create_tag_with_invalid_name(self):
        """Test create tag is not allowed with invalid name"""
        res = self.client.post(LIST_TAG_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tag_filters_only_assigned(self):
        """Test user can query assigned only tags"""
        tag = create_sample_tag(self.user, name="Veg")
        create_sample_tag(self.user, name="Vegan")
        recipe = sample_recipe(self.user, title="Veg Pulav")
        recipe.tags.add(tag)
        res = self.client.get(LIST_TAG_URL, {'assigned_only': 1})
        serializer = TagSerializer(tag)
        self.assertIn(serializer.data, res.data)
        self.assertEqual(len(res.data), 1)

    def test_tag_filters_only_assigned_unique(self):
        """Test user can query unique assigned only tags"""
        tag = create_sample_tag(self.user, name="Lunch")
        recipe = sample_recipe(self.user, title="Veg Pulav")
        recipe2 = sample_recipe(self.user, title='Dal Fry')
        recipe.tags.add(tag)
        recipe2.tags.add(tag)
        serializer = TagSerializer(tag)
        res = self.client.get(LIST_TAG_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer.data, res.data)
