# uase_nigeria/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='nigeria_home'),
    path('about/', views.about, name='nigeria_about'),
    path('services/', views.services, name='nigeria_services'),
    path('case-studies/', views.case_studies, name='nigeria_case_studies'),
    path('partnerships/', views.partnerships, name='nigeria_partnerships'),
    path('contact/', views.contact, name='nigeria_contact'),
]