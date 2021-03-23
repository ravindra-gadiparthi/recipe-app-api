from django.test import TestCasefrom django.contrib.auth import get_user_modelfrom ..models import Tag, Ingredient, Recipe, recipe_image_file_pathfrom unittest.mock import patchdef create_sample_user():    return get_user_model().objects.create_user(        email='test@gmail.com',        password='password'    )class ModelTests(TestCase):    """Models Test Cases"""    def test_create_user_with_email_success(self):        """Test creating user with an email is successful"""        email = 'test@example.com'        password = 'password'        user = get_user_model().objects.create_user(            email=email, password=password        )        self.assertEqual(user.email, email)        self.assertTrue(user.check_password(password))    def test_create_user_with_email_normalized_success(self):        """Test create user with normalized email"""        email = "test@Example.com"        password = 'password'        user = get_user_model().objects.create_user(            email=email,            password=password        )        self.assertEqual(user.email, email.lower())    def test_create_user_with_no_email(self):        """Test create user without email raises Value Error"""        with self.assertRaises(ValueError):            get_user_model().objects.create_user(email=None)    def test_create_user_with_no_empty_email(self):        """Test create user with empty email raises Value Error"""        with self.assertRaises(ValueError):            get_user_model().objects.create_user(email='')    def test_create_super_user_with_email(self):        """Test Superuser with email and password"""        email = "test@example.com"        password = "password"        user = get_user_model().objects.create_superuser(            email=email,            password=password        )        self.assertTrue(user.is_staff)        self.assertTrue(user.is_superuser)    def test_tag_class_string_representation(self):        user = create_sample_user()        tag = Tag.objects.create(name='Vegan', user=user)        self.assertEqual(tag.name, str(tag))    def test_Ingredient_class_string_representation(self):        user = create_sample_user()        ingredient = Ingredient.objects.create(name='Tomato', user=user)        self.assertEqual(ingredient.name, str(ingredient))    def test_recipe_str(self):        """Test recipe string representation"""        title = 'Halwa'        user = create_sample_user()        recipe = Recipe.objects.create(            title=title,            user=user,            time_minutes=5,            price=5.00        )        self.assertEquals(recipe.title, title)    @patch('uuid.uuid4')    def test_recipe_image_file_path(self, mock_uuid4):        mock_value = 'mock_filname'        mock_uuid4.return_value = mock_value        file_path = f'uploads/recipe/{mock_value}.jpg'        self.assertEqual(recipe_image_file_path(None, 'test.jpg'), file_path)