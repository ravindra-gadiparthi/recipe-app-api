from django.db import models
import uuid
import os
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin

from simple_history.models import HistoricalRecords

from django.conf import settings


# Create your models here.

def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Create User and saves a new user"""

        if not email:
            raise ValueError("Invalid Email Address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email=email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    custom user model support email
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """User tag model"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)
    history = HistoricalRecords()

    def __str__(self):
        return self.title
