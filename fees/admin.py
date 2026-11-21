from django.contrib import admin

from .models import FeeStructure, Payment


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('title', 'school_class', 'amount', 'due_date')
    list_filter = ('school_class',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'student', 'fee', 'amount', 'method', 'paid_on')
    list_filter = ('method', 'paid_on')
    date_hierarchy = 'paid_on'
