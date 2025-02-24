from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.views import generic
from django.contrib.auth.decorators import login_required


# SHERRIFF: very basic index page created
class IndexView(generic.TemplateView):
    template_name = "recordstar/index.html"
# Create your views here.

@login_required
def add_item(request):
    # Only allow librarians to access this view.
    if request.user.profile.account_type != 'L':
        return HttpResponseForbidden("You do not have permission to access this page.")
    return render(request, 'recordstar/add_item.html')

# recordstar/views.py
from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'dashboard.html')