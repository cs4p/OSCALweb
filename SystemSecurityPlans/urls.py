"""OSCALweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import listControlsView, controlDetailView, system_security_planDetailView, list_system_security_planView

app_name = 'ssp'
urlpatterns = [
    path('', listControlsView.as_view(), name='index'),
    path('control/', listControlsView.as_view(), name='listControlView'),
    path('control/<int:pk>', controlDetailView.as_view(), name='controlDetailView'),
    path('list/', list_system_security_planView.as_view(), name='list_system_security_planView'),
    path('<int:pk>', system_security_planDetailView.as_view(), name='system_security_planDetailView'),
]
