from django.urls import path
from . import views as settings_views 
from .views import MemberSettingsView
from .views import service_worker

app_name = 'settings'

urlpatterns = [
   path("membersettings/", MemberSettingsView.as_view(), name="member-settings"),
   path('service-worker.js', service_worker, name='service-worker'),
]