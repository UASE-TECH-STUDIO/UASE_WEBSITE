# core/urls.py

from django.urls import path
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemap import StaticViewSitemap  # import the sitemap class

# Define all sitemaps
sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('service/<slug:service_slug>/', views.service_detail, name='service_detail'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/<slug:project_slug>/', views.project_detail, name='project_detail'),
    path('resources/', views.resources, name='resources'),
    path('contact/', views.contact, name='contact'),
    path('resume/', views.resume, name='resume'),
    path('upload/', views.upload_file, name='upload_file'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Blog URLs
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),

    # Sitemap URL (for SEO)
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
