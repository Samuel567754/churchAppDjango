from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views

app_name = 'membership'

urlpatterns = [
    # path('dashboard/', views.member_dashboard, name='member_dashboard'),  # Base dashboard
    path('dashboard/home/', views.member_dashboard_home, name='member_dashboard_home'),
    path('dashboard/attendance/', views.member_dashboard_attendance, name='member_dashboard_attendance'),
    path('dashboard/donations/', views.member_dashboard_donations, name='member_dashboard_donations'),
   
    path('dashboard/events/', views.member_dashboard_events, name='member_dashboard_events'),
    path('dashboard/volunteer/', views.member_dashboard_volunteer, name='member_dashboard_volunteer'),
    path('dashboard/volunteer/apply/<int:opportunity_id>/', views.apply_for_volunteer_opportunity, name='apply_for_volunteer_opportunity'),
    path('dashboard/volunteer/withdraw/<int:application_id>/', views.withdraw_from_volunteer_opportunity, name='withdraw_from_volunteer_opportunity'), path('dashboard/ministries/', views.member_dashboard_ministries, name='member_dashboard_ministries'),
    
    
    path('ministries/all/', views.all_ministries, name='all_ministries'), # All ministries
    path('dashboard/ministries/<slug:slug>/', views.ministry_detail, name='ministry_detail'),
    path('dashboard/ministries/', views.member_dashboard_ministries, name='member_dashboard_ministries'),
    
    
    path('dashboard/announcements/', views.member_dashboard_announcements, name='member_dashboard_announcements'),
    path('dashboard/announcements/<int:announcement_id>/', views.announcement_detail, name='announcement_detail'),
    
    
    
    path('families/', views.list_families, name='family_list'),
    path('families/create/', views.create_family, name='create_family'),
    # path('families/<int:pk>/', views.family_detail, name='family_detail'),
    path('family/<int:pk>/detail/', views.family_detail, name='family_detail'),
    path('families/<int:pk>/add_member/', views.add_family_member, name='add_family_member'),
    path('families/<int:pk>/edit/', views.edit_family, name='edit_family'),
    path('member/family/', views.member_family, name='member_family'),
    path('families/<int:family_id>/remove_member/<int:member_id>/', views.remove_family_member, name='remove_family_member'),
    path('families/<int:pk>/delete/', views.delete_family, name='delete_family'),
]










