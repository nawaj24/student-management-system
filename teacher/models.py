from django.db import models
from django.utils.text import slugify


class Teacher(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    teacher_id = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    qualification = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    joining_date = models.DateField()
    address = models.TextField()
    photo = models.ImageField(upload_to='teachers/', blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.first_name}-{self.last_name}-{self.teacher_id}')
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.full_name} ({self.teacher_id})'
