from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models import Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(user_signed_up)
def create_profile(sender, request, user, **kwargs):
    if user.is_superuser:
        return
    # create Profile for each new user, default is patron
    account_type = request.session.pop("account_type", "P")
    Profile.objects.create(user=user, account_type=account_type) #fetches account_type from session, defaults to P if no type provided

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()