from django.contrib import admin

from .models import Department, Subject


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'head')
    search_fields = ('name', 'code')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department')
    list_filter = ('department',)
    filter_horizontal = ('teachers',)
