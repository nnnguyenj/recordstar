from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required


# SHERRIFF: very basic index page created
from users.models import Profile


class IndexView(generic.TemplateView):
    template_name = "recordstar/index.html"
# Create your views here.

@login_required
def update_profile_picture(request):
    if request.method == 'POST' and request.FILES['profile_picture']:
        profile = Profile.objects.get(user=request.user)
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        return redirect(reverse("index"))
    return render(request, "recordstar/upload_picture.html")  # Render a page with the upload form

@login_required
def add_item(request):
    # Only allow librarians to access this view.
    if request.user.profile.account_type != 'L':
        return HttpResponseForbidden("You do not have permission to access this page.")
    return render(request, 'recordstar/add_item.html')