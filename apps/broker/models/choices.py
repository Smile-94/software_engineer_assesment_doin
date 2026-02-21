from django.db import models


# <<------------------------------------Signal Choices---------------------------------------->>
class SignalStatusChoices(models.TextChoices):
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
