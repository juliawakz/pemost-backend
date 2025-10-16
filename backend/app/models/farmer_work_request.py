from app.choices import WorkRequestStatusChoices
from app.models.e_extension import EExtensionOfficer
from app.models.farm import Farm
from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

User = get_user_model()


class FarmerWorkRequest(BaseModel):
    """
    Work request from Farmer to E-Extension Officer. A farmer can request
    an e-extension officer to work on multiple of their farms.
    """
    farms = models.ManyToManyField(
        Farm,
        related_name='farm_work_request_farms',
        help_text=_("Farms included in this work request")
    )
    e_extension = models.ForeignKey(
        EExtensionOfficer,
        on_delete=models.CASCADE,
        related_name='farm_work_request_e_extensions',
    )
    status = models.CharField(
        max_length=20,
        choices=WorkRequestStatusChoices.choices,
        default=WorkRequestStatusChoices.PENDING
    )
    notification_sent = models.BooleanField(
        default=False,
        help_text="Whether email notification has been sent"
    )
    message = models.TextField(
        blank=True,
        null=True,
        help_text="Optional message from farmer to e-extension"
    )
    response_message = models.TextField(
        blank=True,
        null=True,
        help_text="Optional response message when accepting/rejecting"
    )
    responded_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the request was accepted or rejected"
    )

    slug = None
    metadata = None

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Farmer Work Request")
        verbose_name_plural = _("Farmer Work Requests")
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['e_extension', 'status']),
            models.Index(fields=['is_archived', 'status']),
        ]

    def __str__(self):
        farm_names = ", ".join([farm.name for farm in self.farms.all()[:3]])
        if self.farms.count() > 3:
            farm_names += "..."
        return f"{self.get_farmer_name()} → {self.e_extension.user.full_name} ({self.status}) [{farm_names}]"

    def get_farmer_name(self):
        # Assuming all farms belong to the same farmer
        first_farm = self.farms.first()
        return first_farm.user.full_name if first_farm else "Unknown Farmer"

    def accept(self, response_message=None):
        """
        Accept the work request and establish relationship for all included
        farms. Archives the request after acceptance.
        """
        self.status = WorkRequestStatusChoices.ACCEPTED
        self.responded_at = timezone.now()
        if response_message:
            self.response_message = response_message
        self.is_archived = True
        self.save()

        e_ext_profile = self.e_extension
        for farm in self.farms.all():
            farm.e_extensions.add(e_ext_profile)
            farm.is_visible = True
            farm.save()

    def reject(self, response_message=None):
        """
        Reject the work request.
        Archives the request after rejection.
        """
        self.status = WorkRequestStatusChoices.REJECTED
        self.responded_at = timezone.now()
        if response_message:
            self.response_message = response_message
        self.is_archived = True
        self.save()
