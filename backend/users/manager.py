from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset()

    def get_by_natural_key(self, username):
        username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{username_field: username})

    def _create_user(self, first_name, last_name, phone_number, password, **extra_fields):
        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, first_name, last_name, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(first_name, last_name, phone_number, password, **extra_fields)

    def create_superuser(self, first_name, last_name, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(first_name, last_name, phone_number, password, **extra_fields)
