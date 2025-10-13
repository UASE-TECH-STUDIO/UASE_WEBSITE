# uase_nigeria/views.py

from django.shortcuts import render

def home(request):
    return render(request, 'uase_nigeria/home.html', {})

def about(request):
    return render(request, 'uase_nigeria/about.html', {})

def services(request):
    return render(request, 'uase_nigeria/services.html', {})

def case_studies(request):
    return render(request, 'uase_nigeria/case_studies.html', {})

def partnerships(request):
    return render(request, 'uase_nigeria/partnerships.html', {})

def contact(request):
    return render(request, 'uase_nigeria/contact.html', {})