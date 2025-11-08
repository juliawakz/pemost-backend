from django.db import models


class RoleChoices(models.TextChoices):
    SYSTEM_ADMIN = 'SYSTEM_ADMIN', 'System Admin'
    SUPER_EXTENSION = 'SUPER_EXTENSION', 'Super Extension Officer'
    E_EXTENSION = 'E_EXTENSION', 'E-Extension Officer'
    AGRODEALER = 'AGRODEALER', 'Agrodealer'
    FARMER = 'FARMER', 'Farmer'


class LicenceChoices(models.TextChoices):
    FREE = 'FREE', 'Free'
    PREMIUM = 'PREMIUM', 'Premium'
