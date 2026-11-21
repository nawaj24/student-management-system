from django.contrib import admin

from .models import Event, Period


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('section', 'day', 'number', 'subject', 'teacher', 'start_time', 'end_time')
    list_filter = ('day', 'section__school_class')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'start_date', 'end_date')
    list_filter = ('kind',)
