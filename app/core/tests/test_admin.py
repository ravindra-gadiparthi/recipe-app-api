from django.test import TestCase, Clientfrom django.contrib.auth import get_user_modelfrom django.urls import reverseclass AdminSiteTests(TestCase):    """Admin site Tests"""    def setUp(self):        """initial set up for test"""        self.client = Client()        self.admin_user = get_user_model().objects.create_superuser(            email='adminuser@example.com',            password='password',            name='admin'        )        self.client.force_login(self.admin_user)        self.user = get_user_model().objects.create_user(            email='user@example.com',            password='password',            name='user'        )    def test_users_listed(self):        """Test users are listed on admin"""        url = reverse("admin:core_user_changelist")        res = self.client.get(url)        self.assertContains(res, self.user.email)        self.assertContains(res, self.user.name)    def test_user_page_change(self):        """Test that user edit page works"""        url = reverse("admin:core_user_change", args=[self.user.id])        res = self.client.get(url)        self.assertEqual(res.status_code, 200)    def test_user_page_add(self):        """Test that user add page works"""        url = reverse("admin:core_user_add")        res = self.client.get(url)        self.assertEqual(res.status_code, 200)