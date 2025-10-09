from django.db import models


class RoleChoices(models.TextChoices):
    SUPERUSER = 'SUPERUSER', 'Superuser'
    SUPERADMIN = 'SUPERADMIN', 'Superadmin'
    SUPER_EXTENSION = 'SUPER_EXTENSION', 'Super Extension Officer'
    E_EXTENSION = 'E_EXTENSION', 'E-Extension Officer'
    FARMER = 'FARMER', 'Farmer'
    AGRODEALER = 'AGRODEALER', 'Agrodealer'
