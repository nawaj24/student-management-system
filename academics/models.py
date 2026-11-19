from django.db import models
from django.utils.text import slugify

from teacher.models import Teacher


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    head = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments',
    )
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='subjects',
    )
    teachers = models.ManyToManyField(Teacher, blank=True, related_name='subjects')

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.name}'
