from app.choices import WorkRequestStatusChoices
from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from app.models import (
    SuperExtensionOfficer,
    EExtensionOfficer
)

User = get_user_model()


class EExtensionWorkRequest(BaseModel):
    """
    Work request from E-Extension Officer to Super Extension Officer.
    E-Extension chooses specific super-extensions they want to work under.
    """
    e_extension = models.ForeignKey(
        EExtensionOfficer,
        on_delete=models.CASCADE,
        related_name='sent_super_extension_requests',
    )
    super_extension = models.ForeignKey(
        SuperExtensionOfficer,
        on_delete=models.CASCADE,
        related_name='received_e_extension_requests',
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
        # Only one pending request per e-extension/super-extension pair
        constraints = [
            models.UniqueConstraint(
                fields=['e_extension', 'super_extension'],
                condition=models.Q(status='PENDING', is_archived=False),
                name='unique_pending_e_extension_request'
            )
        ]
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['e_extension', 'status']),
            models.Index(fields=['super_extension', 'status']),
            models.Index(fields=['is_archived', 'status']),
        ]

    def __str__(self):
        return f"{self.e_extension.user.full_name} → {self.super_extension.user.full_name} ({self.status})"

    def accept(self, response_message=None):
        """
        Accept the work request and establish relationship.
        Archives the request after acceptance.
        """
        self.status = WorkRequestStatusChoices.ACCEPTED
        self.responded_at = timezone.now()
        if response_message:
            self.response_message = response_message
        self.is_archived = True  # Archive the request
        self.save()

        # Add e-extension to super extension's managed list
        e_ext_profile = self.e_extension
        super_ext_profile = self.super_extension
        e_ext_profile.super_extensions.add(super_ext_profile)
        e_ext_profile.is_visible = True
        e_ext_profile.save()

    def reject(self, response_message=None):
        """
        Reject the work request.
        Archives the request after rejection.
        """
        self.status = WorkRequestStatusChoices.REJECTED
        self.responded_at = timezone.now()
        if response_message:
            self.response_message = response_message
        self.is_archived = True  # Archive the request
        self.save()
