from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views import generic
from .models import system_control

class listControlsView(generic.ListView):
    # template_name = 'polls/index.html'
    context_object_name = 'system_control'

    def get_queryset(self):
        return system_control.objects.all()


class controlDetailView(generic.DetailView):
    model = system_control
    # template_name = 'polls/detail.html'
