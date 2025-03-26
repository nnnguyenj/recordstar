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
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics/')
    created_at = models.DateTimeField(auto_now_add=True)
    friends = models.ManyToManyField("self", symmetrical=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_account_type_display()})"
    
class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  #link to user who owns the collection
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    release_date = models.DateField()
    rating = models.IntegerField()  #1-10 scale
    review = models.TextField()

    def __str__(self):
        return f"{self.title} by {self.artist}"

