from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, authenticate, login
from users.models import CD
from django.contrib import messages

# SHERRIFF: very basic index page created
from users.models import Profile


class IndexView(generic.TemplateView):
    template_name = "recordstar/upload_picture.html"
# Create your views here.

@login_required
def first_time_setup(request):
    if request.method == 'POST' and 'profile_picture' in request.FILES:
        profile = Profile.objects.get(user=request.user)
        profile.image = request.FILES['profile_picture']
        profile.save()

        # Re-authenticate the user
        user = authenticate(request, username=request.user.username)
        if user:
            login(request, user)

        return redirect("dashboard")

    return render(request, "recordstar/first_time_setup.html")


@login_required
def search_cd_by_code(request):
    if request.method == 'POST':
        code = request.POST.get('unique_code').strip().upper()
        try:
            cd = CD.objects.get(unique_code=code, owner=request.user)
            return render(request, 'recordstar/cd_detail.html', {'cd': cd})
        except CD.DoesNotExist:
            messages.error(request, "No CD found with that code.")

    return render(request, 'recordstar/search_cd.html')
# recordstar/views.py
from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'dashboard.html')

def anon_user_welcome(request):
    return render(request, 'recordstar/anon_user_welcome.html')
