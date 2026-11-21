from django.db import models

from teacher.models import Teacher


class SchoolClass(models.Model):
    name = models.CharField(max_length=50, unique=True)
    order = models.PositiveSmallIntegerField(default=0, help_text='1 for Class 1, 10 for Class 10')

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'classes'

    def __str__(self):
        return self.name


class Section(models.Model):
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='sections',
    )
    name = models.CharField(max_length=10)
    class_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_sections',
    )
    room = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['school_class__order', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['school_class', 'name'],
                name='unique_section_per_class',
            ),
        ]

    def __str__(self):
        return f'{self.school_class.name} - {self.name}'
