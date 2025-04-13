from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from users.models import Profile


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                profile = user.profile
                if profile.image and not profile.image.name.endswith("default.jpg"):
                    print("[CustomAccountAdapter] ✅ Redirecting to dashboard")
                    return "/dashboard/"
                else:
                    print("[CustomAccountAdapter] 🖼️ Needs profile picture")
                    return "/recordstar/update_picture/"
            except Profile.DoesNotExist:
                print("[CustomAccountAdapter] ❌ No profile found")
                return "/recordstar/update_picture/"
        return super().get_login_redirect_url(request)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                profile = user.profile
                if profile.image and not profile.image.name.endswith("default.jpg"):
                    print("[CustomSocialAccountAdapter] ✅ Redirecting to dashboard")
                    return "/dashboard/"
                else:
                    print("[CustomSocialAccountAdapter] 🖼️ Needs profile picture")
                    return "/recordstar/update_picture/"
            except Profile.DoesNotExist:
                print("[CustomSocialAccountAdapter] ❌ No profile found")
                return "/recordstar/update_picture/"
        return super().get_login_redirect_url(request)
