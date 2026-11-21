from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from classroom.models import SchoolClass
from student.models import Student


class FeeStructure(models.Model):
    """One fee that every student of a class must pay, e.g. 'Tuition · Mangsir'."""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='fees')
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                                 validators=[MinValueValidator(Decimal('1'))])
    due_date = models.DateField()

    class Meta:
        ordering = ['due_date', 'school_class__order']
        constraints = [
            models.UniqueConstraint(fields=['school_class', 'title'], name='unique_fee_per_class'),
        ]

    def __str__(self):
        return f'{self.title} · {self.school_class} · Rs. {self.amount}'


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'cash', 'Cash'
        ESEWA = 'esewa', 'eSewa'
        KHALTI = 'khalti', 'Khalti'
        BANK = 'bank', 'Bank Transfer'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    fee = models.ForeignKey(FeeStructure, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2,
                                 validators=[MinValueValidator(Decimal('1'))])
    method = models.CharField(max_length=10, choices=Method.choices, default=Method.CASH)
    paid_on = models.DateField(default=timezone.localdate)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )

    class Meta:
        ordering = ['-paid_on', '-pk']

    @property
    def receipt_number(self):
        return f'RCP-{self.pk:05d}'

    def __str__(self):
        return f'{self.receipt_number} · {self.student} · Rs. {self.amount}'
