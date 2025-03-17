from django.urls import path
from . import views as settings_views 
from .views import MemberSettingsView

app_name = 'settings'

urlpatterns = [
   path("membersettings/", MemberSettingsView.as_view(), name="member-settings"),
]