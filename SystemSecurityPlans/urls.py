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
from .views import *

app_name = 'ssp'
urlpatterns = [
    path('nist_control/list', nist_control_list_view.as_view(), name='nist_control_list_view'),
    path('nist_control/<int:pk>', nist_control_detail_view.as_view(), name='nist_control_detail_view'),
    path('control/list', system_control_list_view.as_view(), name='system_control_list_view'),
    path('control/<int:pk>', system_control_detail_view.as_view(), name='system_control_detail_view'),
    path('', system_security_plan_list_view.as_view(), name='system_security_plan_list_view'),
    path('<int:pk>', system_security_plan_detail_view.as_view(), name='system_security_plan_detail_view'),
]
