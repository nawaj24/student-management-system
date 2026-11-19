from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from home_auth.models import CustomUser
from teacher.models import Teacher
from teacher.tests import TEACHER_FORM, make_user
from .models import Department, Subject


class AcademicsTests(TestCase):
    """Departments and subjects (Episode 4)."""

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='admin@school.com', email='admin@school.com', password='StrongPass123')
        self.teacher = Teacher.objects.create(**TEACHER_FORM)
        self.science = Department.objects.create(name='Science', code='SCI')
        self.client.force_login(self.admin)

    def test_add_department_makes_slug_and_upper_case_code(self):
        response = self.client.post(reverse('add_department'), {'name': 'Social Studies', 'code': 'soc'})
        self.assertRedirects(response, reverse('department_list'))
        department = Department.objects.get(name='Social Studies')
        self.assertEqual(department.slug, 'social-studies')
        self.assertEqual(department.code, 'SOC')

    def test_add_subject_with_teachers(self):
        self.client.post(reverse('add_subject'), {
            'name': 'Physics', 'code': 'sci102', 'department': self.science.pk,
            'teachers': [self.teacher.pk],
        })
        subject = Subject.objects.get(code='SCI102')
        self.assertEqual(list(subject.teachers.all()), [self.teacher])
        page = self.client.get(reverse('teacher_detail', args=[self.teacher.slug]))
        self.assertContains(page, 'Physics')

    def test_department_with_subjects_cannot_be_deleted(self):
        Subject.objects.create(name='Physics', code='SCI102', department=self.science)
        response = self.client.post(reverse('delete_department', args=[self.science.slug]), follow=True)
        self.assertTrue(Department.objects.filter(pk=self.science.pk).exists())
        self.assertContains(response, 'still has subjects')

    def test_subject_list_filter_by_department(self):
        maths = Department.objects.create(name='Mathematics', code='MTH')
        Subject.objects.create(name='Physics', code='SCI102', department=self.science)
        Subject.objects.create(name='Algebra', code='MTH101', department=maths)
        response = self.client.get(reverse('subject_list'), {'department': 'mathematics'})
        self.assertContains(response, 'Algebra')
        self.assertNotContains(response, 'Physics')

    def test_permissions(self):
        self.client.force_login(make_user('sita@school.com', is_teacher=True))
        self.assertEqual(self.client.get(reverse('department_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('add_subject')).status_code, 403)
        self.client.force_login(make_user('aarav@school.com', is_student=True))
        self.assertEqual(self.client.get(reverse('subject_list')).status_code, 403)

    def test_seed_academics_links_teachers(self):
        call_command('seed_teachers', stdout=open('/dev/null', 'w'))
        call_command('seed_academics', stdout=open('/dev/null', 'w'))
        call_command('seed_academics', stdout=open('/dev/null', 'w'))  # safe to run twice
        self.assertEqual(Department.objects.count(), 4)  # 'SCI' already existed
        self.assertEqual(Subject.objects.count(), 8)
        physics = Subject.objects.get(name='Physics')
        self.assertEqual(physics.teachers.get().first_name, 'Dinesh')
