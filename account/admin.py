from django.contrib import admin
from django.utils.html import format_html
from .models import Church


class ChurchAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone_number', 'email', 'website', 'logo_preview']
    search_fields = ['name', 'address']
    list_filter = ['name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = [
        ('General Information', {
            'fields': ['name', 'description', 'logo', ],
            'classes': ['wide', 'extrapretty'],  # Jazmin classes for styling
        }),
        ('Contact Details', {
            'fields': ['address', 'phone_number', 'email', 'website'],
            'classes': ['collapse', 'extrapretty'] , # Jazmin classes to collapse this section
        }),
       ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'created_by', 'updated_by'],
            'classes': ['collapse']  # Default Django classes for collapsing the section
        }),
    ]

    def save_model(self, request, obj, form, change):
        if not change:
          obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width:50px;" />', obj.logo.url)
        return "No Logo"

    logo_preview.short_description = "Logo"


admin.site.register(Church, ChurchAdmin)