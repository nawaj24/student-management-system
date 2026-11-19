from django.core.exceptions import ValidationError
from django.db import models

from academics.models import Subject
from classroom.models import SchoolClass
from student.models import Student


class Exam(models.Model):
    name = models.CharField(max_length=100)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='exams')
    start_date = models.DateField()
    full_marks = models.PositiveSmallIntegerField(default=100)
    pass_marks = models.PositiveSmallIntegerField(default=40)

    class Meta:
        ordering = ['-start_date', 'school_class__order']
        constraints = [
            models.UniqueConstraint(fields=['name', 'school_class'], name='unique_exam_per_class'),
        ]

    def clean(self):
        if self.pass_marks > self.full_marks:
            raise ValidationError({'pass_marks': 'Pass marks cannot be more than full marks.'})

    def __str__(self):
        return f'{self.name} · {self.school_class}'


class Mark(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='marks')
    marks_obtained = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['exam', 'student', 'subject'], name='one_mark_per_subject'),
        ]

    def __str__(self):
        return f'{self.student} · {self.subject.name} · {self.marks_obtained}'
