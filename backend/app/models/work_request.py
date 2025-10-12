from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from base.models import BaseModel
from app.choices import WorkRequestStatusChoices

User = get_user_model()


class EExtensionWorkRequest(BaseModel):
    """
    Work request from E-Extension Officer to Super Extension Officer.
    E-Extension chooses specific super-extensions they want to work under.
    """
    e_extension = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_super_extension_requests',
        limit_choices_to={'role': 'E_EXTENSION'}
    )
    super_extension = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_e_extension_requests',
        limit_choices_to={'role': 'SUPER_EXTENSION'}
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
        help_text="Optional message from e-extension to super extension"
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
        verbose_name = _("E-Extension Work Request")
        verbose_name_plural = _("E-Extension Work Requests")
        unique_together = [['e_extension', 'super_extension', 'status']]
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['e_extension', 'status']),
            models.Index(fields=['super_extension', 'status']),
        ]

    def __str__(self):
        return f"{self.e_extension.full_name} → {self.super_extension.full_name} ({self.status})"

    def accept(self, response_message=None):
        """Accept the work request and establish relationship"""
        from django.utils import timezone
        self.status = WorkRequestStatusChoices.ACCEPTED
        self.responded_at = timezone.now()
        if response_message:
            self.response_message = response_message
        self.save()

        # Add e-extension to super extension's managed list
        e_ext_profile = self.e_extension.e_extension_profile
        super_ext_profile = self.super_extension.super_extension_profile
        e_ext_profile.super_extensions.add(super_ext_profile)
        e_ext_profile.is_visible = True
        e_ext_profile.save()

    def reject(self, response_message=None):
        """Reject the work request"""
        from django.utils import timezone
        self.status = WorkRequestStatusChoices.REJECTED
        self.responded_at = timezone.now()
        if response_message:
            self.response_message = response_message
        self.save()


class FarmerWorkRequest(BaseModel):
    """
    Work request from Farmer to E-Extension Officer.
    Farmer chooses specific e-extensions they want to work under.
    """
    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_e_extension_requests',
        limit_choices_to={'role': 'FARMER'}
    )
    e_extension = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_farmer_requests',
        limit_choices_to={'role': 'E_EXTENSION'}
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
        unique_together = [['farmer', 'e_extension', 'status']]
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['farmer', 'status']),
            models.Index(fields=['e_extension', 'status']),
        ]

    def __str__(self):
        return f"{self.farmer.full_name} → {self.e_extension.full_name} ({self.status})"

    def accept(self, response_message=None):
        """Accept the work request and establish relationship"""
        from django.utils import timezone
        from farms.models import Farm

        self.status = WorkRequestStatusChoices.ACCEPTED
        self.responded_at = timezone.now()
        if response_message:
            self.response_message = response_message
        self.save()

        # Add e-extension to farmer's farms
        e_ext_profile = self.e_extension.e_extension_profile
        farmer_farms = Farm.objects.filter(owner=self.farmer)
        for farm in farmer_farms:
            farm.e_extensions.add(e_ext_profile)
            farm.is_visible = True
            farm.save()

    def reject(self, response_message=None):
        """Reject the work request"""
        from django.utils import timezone
        self.status = WorkRequestStatusChoices.REJECTED
        self.responded_at = timezone.now()
        if response_message:
            self.response_message = response_message
        self.save()
