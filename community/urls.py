from django.urls import path
from . import views
from .views import devotional_detail_json

app_name = 'community'

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    
    path('devotionals/<slug:slug>/data/', devotional_detail_json, name='devotional_detail_json'),
    
    path('calendar/events/json/', views.events_json, name='events_json'),
    path('calendar/event/<slug:slug>/', views.church_calendar_detail, name='church_calendar_detail'),
    
    path('ministries/', views.ministries, name='ministries'),
    path('give/', views.give, name='give'), 
    path('faq/', views.faq_view, name='faq'),
    path('gallery/', views.gallery, name='gallery'),
    path('devotionals/', views.devotionals, name='devotionals'),
    path('live-streams/', views.live_streams, name='live_streams'),
]
