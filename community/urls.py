from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('ministries/', views.ministries, name='ministries'),
    path('give/', views.give, name='give'), 
    path('faq/', views.faq_view, name='faq'),
    path('gallery/', views.gallery, name='gallery'),
]
