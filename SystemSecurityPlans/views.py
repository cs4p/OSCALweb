from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views import generic
from .models import implementedRequirements

class listControlsView(generic.ListView):
    # template_name = 'polls/index.html'
    context_object_name = 'implementedRequirements'

    def get_queryset(self):
        return implementedRequirements.objects.all()


class controlDetailView(generic.DetailView):
    model = implementedRequirements
    # template_name = 'polls/detail.html'
