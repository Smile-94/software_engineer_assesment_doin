from django.db import models

from apps.common.functions.unique_id_generator import generate_custom_id
from apps.common.models import BaseModel, TimeStampedModel
from apps.user.models.user_model import User


# <<--------------------------------- Broker Account Model --------------------------------->>
class BrokerAccount(BaseModel, TimeStampedModel):
    """User's broker account information"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="broker_account")
    account_name = models.CharField(max_length=100, blank=True, null=True)
    account_id = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=255, unique=True)

    class Meta:
        app_label = "broker"
        verbose_name = "Broker Account"
        verbose_name_plural = "Broker Accounts"
        db_table = "broker_account"
        indexes = [
            models.Index(fields=["user", "active_status"]),
            models.Index(fields=["account_id"]),
        ]

    def clean(self):
        if not self.account_id:
            self.account_id = generate_custom_id("BRk", "account_id", self.__class__)
        return super().clean()

    def save(self, *args, **kwargs):
        """
        Override save to ensure clean is called before saving.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.account_id}"

    def __repr__(self):
        return f"<- {self.__class__.__name__}: {self.user.username} - {self.account_id}->"
