from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from home_auth.models import CustomUser
from school.tests import STUDENT_FORM, make_user
from student.models import Student
from .models import SchoolClass, Section


class ClassroomTests(TestCase):
    """Classes and sections (Episode 5)."""

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='admin@school.com', email='admin@school.com', password='StrongPass123')
        self.client.force_login(self.admin)
        call_command('seed_classes', stdout=StringIO())
        self.ten_a = Section.objects.get(school_class__name='Class 10', name='A')

    def test_seed_classes_runs_twice_safely(self):
        call_command('seed_classes', stdout=StringIO())
        self.assertEqual(SchoolClass.objects.count(), 10)
        self.assertEqual(Section.objects.count(), 20)
        self.assertEqual(str(self.ten_a), 'Class 10 - A')

    def test_classes_sorted_by_order_not_text(self):
        names = list(SchoolClass.objects.values_list('name', flat=True))
        self.assertEqual(names[:3], ['Class 1', 'Class 2', 'Class 3'])
        self.assertEqual(names[-1], 'Class 10')

    def test_duplicate_section_is_rejected(self):
        response = self.client.post(reverse('add_section'), {
            'school_class': self.ten_a.school_class.pk, 'name': 'a',
        })
        self.assertEqual(response.status_code, 200)  # form shown again with an error
        self.assertContains(response, 'already exists')
        self.assertEqual(Section.objects.filter(school_class=self.ten_a.school_class).count(), 2)

    def test_add_student_into_a_section(self):
        self.client.post(reverse('add_student'), dict(STUDENT_FORM, section=self.ten_a.pk))
        student = Student.objects.get(student_id='S001')
        self.assertEqual(student.section, self.ten_a)
        page = self.client.get(reverse('section_detail', args=[self.ten_a.pk]))
        self.assertContains(page, 'Ram Sharma')
        self.assertContains(self.client.get(reverse('class_list')), 'Class 10')

    def test_permissions(self):
        self.client.force_login(make_user('sita@school.com', is_teacher=True))
        self.assertEqual(self.client.get(reverse('class_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('add_section')).status_code, 403)
        self.client.force_login(make_user('aarav@school.com', is_student=True))
        self.assertEqual(self.client.get(reverse('class_list')).status_code, 403)
