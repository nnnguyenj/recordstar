from django.db import models
from django.contrib.auth.models import User
import uuid

class CD(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=100)
    release_year = models.IntegerField(null=True, blank=True)
    genre = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='cd_covers/', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cds')
    date_added = models.DateTimeField(auto_now_add=True)
    unique_code = models.CharField(max_length=12, unique=True, editable=False, blank=True)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.artist}"
