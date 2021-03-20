# recipe-app-api## Commands to build docker images`###Using docker compose ```bashdocker-compose build```### Create Django Project```bashdocker-compose run app sh -c "django-admin.py startproject app ."```### Run Python test_add_numbers```bashdocker-compose run app sh -c "python manage.py test"```### Creating Migration Script ```bashdocker-compose run app sh -c "python manage.py makemigrations core"```### Migrating scripts```bashdocker-compose run app sh -c "python manage.py migrate"```### Running app```bashdocker-compose up```##Useful linksCreating Custom User Model [AbstractBaseUser](https://docs.djangoproject.com/en/2.1/topics/auth/customizing/#django.contrib.auth.models.AbstractBaseUser)[PermissionsMixin](https://docs.djangoproject.com/en/2.1/topics/auth/customizing/#django.contrib.auth.models.PermissionsMixin)[BaseUserManager](https://docs.djangoproject.com/en/2.1/topics/auth/customizing/#django.contrib.auth.models.BaseUserManager)[ModelAdmin.fieldsets](https://docs.djangoproject.com/en/2.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets)