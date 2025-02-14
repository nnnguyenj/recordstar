from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic


# SHERRIFF: very basic index page created
class IndexView(generic.TemplateView):
    template_name = "recordstar/index.html"
# Create your views here.
