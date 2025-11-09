from django.db import models


class WorkRequestStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    REJECTED = 'REJECTED', 'Rejected'


class AlertStatusChoices(models.TextChoices):
    YELLOW = 'YELLOW', 'Yellow'
    RED = 'RED', 'Red'
    GREEN = 'GREEN', 'Green'
    NONE = 'NONE', 'None'
