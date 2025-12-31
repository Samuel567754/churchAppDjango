from django.urls import path
from . import views as settings_views 
from .views import MemberSettingsView
# from .views import service_worker

app_name = 'settings'

urlpatterns = [
   path("membersettings/", MemberSettingsView.as_view(), name="member-settings"),
   # path('service-worker.js', service_worker, name='service-worker'),
   
   # Keep-Alive endpoints (no authentication required)
   path('keep-alive/', settings_views.keep_alive, name='keep-alive'),
   path('health/', settings_views.health_check, name='health-check'),
]