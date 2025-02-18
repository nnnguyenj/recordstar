from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models import Profile

@receiver(user_signed_up)
def create_profile(sender, request, user, **kwargs):
    # create Profile for each new user, default is patron
    Profile.objects.create(user=user, account_type='P')
