from django.urls import path
from . import views


app_name = 'worship'

urlpatterns = [
    path('sermons/', views.sermons, name='sermons'),
    path('sermons/<slug:slug>/', views.sermon_detail, name='sermon_detail'),
    path('series/<slug:slug>/', views.series_detail, name='series_detail'),
    path('tags/<slug:slug>/', views.tag_detail, name='tag_detail'),

    
    path('dashboard/prayer-requests/', views.prayer_requests, name='prayer_requests'),
    path('dashboard/prayer-requests/new/', views.prayer_request_create, name='prayer_request_create'),
    path('dashboard/prayers/edit/<int:pk>/', views.prayer_request_update, name='prayer_request_update'),
    path('dashboard/prayers/delete/<int:pk>/', views.prayer_request_delete, name='prayer_request_delete'),
    path('dashboard/my-appointments/', views.member_appointments, name='member_appointments'),
    path('respond-appointment/<int:appointment_id>/', views.respond_appointment, name='respond_appointment'),
    path("appointment/delete/<int:appointment_id>/", views.delete_appointment, name="delete_appointment"),
    path('weekly-appointments/', views.weekly_service_appointments, name='weekly_service_appointments'),
    path('appointment/history/', views.appointment_history, name='appointment_history'),
    path('weekly-attendance/', views.weekly_service_attendance, name='weekly_attendance'),
    path('export-attendance/', views.export_attendance_csv, name='export_attendance'),
    path('attendance/pdf/', views.generate_pdf, name='generate_pdf'),
    path('attendance/doc/', views.generate_doc, name='generate_doc'),
    path('attendance/attendance_history/', views.attendance_history, name='attendance_history'),
    path('attendance/history/doc/', views.generate_attendance_history_doc, name='generate_attendance_history_doc'),
    path('attendance/history/pdf/', views.generate_attendance_history_pdf, name='generate_attendance_history_pdf'),
    path('attendance/history/csv/', views.export_attendance_history_csv, name='export_attendance_history_csv'),
    
    path('resources/list', views.resource_list, name='resource_list'),
    path('resources/<int:pk>/download/', views.resource_download, name='resource_download'),
    
]
