from django import forms
from django.forms import ModelForm
from SystemSecurityPlans import models as ssp

class SystemSecurityPlan(ModelForm):
    class Meta:
        model = ssp.systemSecurityPlan
        fields = '__all__'
