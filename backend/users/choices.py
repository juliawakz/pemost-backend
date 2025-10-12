from django.db import models


class RoleChoices(models.TextChoices):
    E_EXTENSION = 'E_EXTENSION', 'E-Extension Officer'
    SYSTEMADMIN = 'SYSTEMADMIN', 'System Admin'
    SUPER_EXTENSION = 'SUPER_EXTENSION', 'Super Extension Officer'
    FARMER = 'FARMER', 'Farmer'
    AGRODEALER = 'AGRODEALER', 'Agrodealer'


class WorkRequestStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    REJECTED = 'REJECTED', 'Rejected'
