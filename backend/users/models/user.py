import logging

from base.models import BaseModel
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from phonenumber_field.modelfields import PhoneNumberField
from users.choices import RoleChoices
from users.manager import UserManager

logger = logging.getLogger(__name__)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(
        max_length=30,
        null=False,
        blank=False,
    )
    last_name = models.CharField(
        max_length=30,
        null=False,
        blank=False,
    )
    id_number = models.CharField(
        unique=True,
        null=True,
        blank=True
    )
    phone_number = PhoneNumberField(
        unique=True,
        null=False,
        blank=False,
    )
    email = models.EmailField(
        unique=True,
        max_length=50,
        null=False,
        blank=False,
    )
    profile_photo = models.ImageField(
        upload_to="profile",
        null=True,
        blank=True
    )
    is_staff = models.BooleanField(
        default=False,
    )
    last_login = models.DateTimeField(
        _("last login"), default=timezone.now
    )
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices
    )
    is_verified = models.BooleanField(
        blank=False,
        null=False,
        default=False
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone_number"
    ]

    slug = None
    metadata = None

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        get_latest_by = ("-updated_at",)

    def __str__(self):
        return f"{self.full_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def profile_photo_url(self):
        if self.profile_photo:
            return f"{settings.SERVER_HOST}{self.profile_photo.url}"
        return None

    def is_systemadmin(self):
        return self.role == RoleChoices.SYSTEMADMIN

    def is_superextension(self):
        return self.role == RoleChoices.SUPER_EXTENSION

    def is_eextension(self):
        return self.role == RoleChoices.E_EXTENSION

    def is_agrodealer(self):
        return self.role == RoleChoices.AGRODEALER

    def is_farmer(self):
        return self.role == RoleChoices.FARMER

    # Legacy aliases for backward compatibility
    def is_super_extension(self):
        return self.is_superextension()

    def is_e_extension(self):
        return self.is_eextension()
