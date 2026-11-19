from django.contrib import admin

from .models import SchoolClass, Section


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    inlines = [SectionInline]
