from django.db import models
from django.contrib.auth.models import User

class CD(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=100)
    release_year = models.IntegerField(null=True, blank=True)
    genre = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='cd_covers/', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cds')
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} by {self.artist}"
