from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
def get_default_profile_image():
    return 'default.jpg'

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
    is_collection_public = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_account_type_display()})"
    
class FriendActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_activities")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="added_by")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} added {self.friend.username}"

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
    
    # Rating fields
    user_rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.artist}"
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cd = models.ForeignKey(CD, on_delete=models.CASCADE, related_name='ratings')
    rating_value = models.IntegerField()  # e.g., 1-10 scale
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} rated {self.cd.title} ({self.rating_value})"
    
class Collection(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    name = models.CharField(max_length=100)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cds = models.ManyToManyField(CD, blank=True, related_name="collections")

    def __str__(self):
        return f"{self.name} ({'Public' if self.is_public else 'Private'})"
    
class Library(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="library")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Library"