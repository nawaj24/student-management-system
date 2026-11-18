from django.contrib import admin

from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'first_name', 'last_name', 'subject', 'mobile_number')
    search_fields = ('first_name', 'last_name', 'teacher_id', 'subject')
