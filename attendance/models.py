from django.conf import settings
from django.db import models
from django.utils import timezone

from student.models import Student


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'P', 'Present'
        ABSENT = 'A', 'Absent'
        LATE = 'L', 'Late'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.PRESENT)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['student', 'date'], name='one_attendance_per_day'),
        ]

    def __str__(self):
        return f'{self.student} · {self.date} · {self.get_status_display()}'
