from django.contrib.auth import get_user_modelfrom django.test import TestCasefrom django.urls import reversefrom rest_framework import statusfrom rest_framework.test import APIClientfrom core.models import Tagfrom ..serializers import TagSerializerLIST_TAG_URL = reverse('recipe:tag-list')class PublicApiTestCase(TestCase):    def setUp(self):        self.client = APIClient()    def test_list_tags_without_authentication(self):        """Test list tags is not accessible without authentication"""        res = self.client.get(LIST_TAG_URL)        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)    def test_create_tags_without_authentication(self):        """Test create tags is not accessible without authentication"""        res = self.client.post(LIST_TAG_URL, {})        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)class PrivateTapApiTestCases(TestCase):    def setUp(self):        self.client = APIClient()        self.user = get_user_model().objects.create_user(            'test@example.com',            'password',        )        self.client.force_authenticate(self.user)    def test_list_tags_with_authentication(self):        """Test authenticated uses can query tags"""        Tag.objects.create(user=self.user, name="tag1")        Tag.objects.create(user=self.user, name="tag2")        tags = Tag.objects.all().order_by('-name')        serializer = TagSerializer(tags, many=True)        res = self.client.get(LIST_TAG_URL)        self.assertEqual(res.status_code, status.HTTP_200_OK)        self.assertEqual(res.data, serializer.data)    def test_authenticated_users_queries(self):        user1 = get_user_model().objects.create_user(            'test1@gmail.com',            'password'        )        Tag.objects.create(user=user1, name='tag1')        tag = Tag.objects.create(user=self.user, name='tag2')        res = self.client.get(LIST_TAG_URL)        self.assertEqual(len(res.data), 1)        self.assertEqual(res.data[0]['name'], tag.name)    def test_authenticated_user_create_tags(self):        payload = {'name': 'Tag1'}        res = self.client.post(LIST_TAG_URL, payload)        exists = Tag.objects.filter(user=self.user, name=payload['name']).exists()        self.assertEquals(res.status_code, status.HTTP_201_CREATED)        self.assertTrue(exists)        self.assertEquals(res.data['name'], payload['name'])    def test_create_tag_with_invalid_name(self):        """Test create tag is not allowed with invalid name"""        res = self.client.post(LIST_TAG_URL, {})        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)