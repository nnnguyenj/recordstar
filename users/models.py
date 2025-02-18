from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('P', 'Patron'),
        ('L', 'Librarian'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=1, choices=ACCOUNT_TYPE_CHOICES, default='P')

    def __str__(self):
        return f"{self.user.username} ({self.get_account_type_display()})"

