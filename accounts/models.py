from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_curator = models.BooleanField(default=False)

    class Meta:
        db_table = "accounts_user"
