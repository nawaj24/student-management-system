from django.contrib import admin

from .models import Exam, Mark


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_class', 'start_date', 'full_marks', 'pass_marks')
    list_filter = ('school_class',)


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'subject', 'marks_obtained')
    list_filter = ('exam', 'subject')
