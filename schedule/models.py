from django.core.exceptions import ValidationError
from django.db import models

from academics.models import Subject
from classroom.models import Section
from teacher.models import Teacher


class Period(models.Model):
    """One box of the timetable: Class 4 - A, Sunday, 1st period, Maths."""

    class Day(models.IntegerChoices):
        SUNDAY = 0, 'Sunday'  # school week in Nepal: Sunday to Friday
        MONDAY = 1, 'Monday'
        TUESDAY = 2, 'Tuesday'
        WEDNESDAY = 3, 'Wednesday'
        THURSDAY = 4, 'Thursday'
        FRIDAY = 5, 'Friday'

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='periods')
    day = models.PositiveSmallIntegerField(choices=Day.choices)
    number = models.PositiveSmallIntegerField(help_text='1 for the 1st period, 2 for the 2nd ...')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='periods')
    teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='periods',
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['day', 'number']
        constraints = [
            models.UniqueConstraint(fields=['section', 'day', 'number'], name='one_subject_per_slot'),
            models.UniqueConstraint(
                fields=['teacher', 'day', 'number'],
                condition=models.Q(teacher__isnull=False),
                name='teacher_in_one_place',
                violation_error_message='This teacher already has a class in this period.',
            ),
        ]

    def clean(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError({'end_time': 'End time must be after the start time.'})

    def __str__(self):
        return f'{self.section} · {self.get_day_display()} · Period {self.number}'


class Event(models.Model):
    class Kind(models.TextChoices):
        HOLIDAY = 'holiday', 'Holiday'
        EVENT = 'event', 'Event'
        EXAM = 'exam', 'Exam'

    title = models.CharField(max_length=150)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.EVENT)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text='Leave empty for a one-day event')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['start_date']

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'End date cannot be before the start date.'})

    @property
    def last_day(self):
        return self.end_date or self.start_date

    def __str__(self):
        return f'{self.title} · {self.start_date}'
