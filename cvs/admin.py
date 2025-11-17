from django.contrib import admin
from .models import CV, Job

# Hiển thị CV trong admin
@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'full_name', 'email', 'phone', 'skills', 'created_at'
    )
    search_fields = ('full_name', 'email', 'skills')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


# Hiển thị Job trong admin
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company', 'created_at', 'fetched_at'
    )
    search_fields = ('title', 'company', 'labels')
    list_filter = ('company', 'created_at')
    ordering = ('-created_at',)
