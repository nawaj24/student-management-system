import datetime
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from classroom.models import Section
from home_auth.models import CustomUser
from school.tests import make_user
from student.models import Student
from .models import Attendance


class AttendanceTests(TestCase):
    """Attendance (Episode 6)."""

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='admin@school.com', email='admin@school.com', password='StrongPass123')
        self.client.force_login(self.admin)
        call_command('seed_classes', stdout=StringIO())
        call_command('seed_students', count=20, stdout=StringIO())
        self.section = Section.objects.filter(students__isnull=False).distinct().first()
        self.students = list(self.section.students.all())
        self.today = timezone.localdate()
        self.url = f"{reverse('mark_attendance')}?section={self.section.pk}&date={self.today}"

    def post_statuses(self, status_for_first='A'):
        data = {f'status_{s.pk}': 'P' for s in self.students}
        data[f'status_{self.students[0].pk}'] = status_for_first
        return self.client.post(self.url, data)

    def test_mark_saves_one_row_per_student(self):
        self.post_statuses('A')
        self.assertEqual(Attendance.objects.count(), len(self.students))
        self.assertEqual(Attendance.objects.get(student=self.students[0]).status, 'A')
        self.assertEqual(Attendance.objects.get(student=self.students[0]).marked_by, self.admin)

    def test_marking_again_updates_instead_of_duplicating(self):
        self.post_statuses('A')
        self.post_statuses('L')
        self.assertEqual(Attendance.objects.count(), len(self.students))
        self.assertEqual(Attendance.objects.get(student=self.students[0]).status, 'L')

    def test_future_date_is_rejected(self):
        tomorrow = self.today + datetime.timedelta(days=1)
        url = f"{reverse('mark_attendance')}?section={self.section.pk}&date={tomorrow}"
        response = self.client.post(url, {}, follow=True)
        self.assertContains(response, 'future date')
        self.assertFalse(Attendance.objects.exists())

    def test_monthly_report_percentage(self):
        student = self.students[0]
        for offset, status in enumerate(['P', 'P', 'L', 'A']):
            Attendance.objects.create(student=student, date=self.today.replace(day=1) + datetime.timedelta(days=offset),
                                      status=status)
        url = reverse('attendance_report')
        response = self.client.get(url, {'section': self.section.pk, 'month': f'{self.today:%Y-%m}'})
        row = next(r for r in response.context['rows'] if r['student'] == student)
        self.assertEqual((row['total'], row['percent']), (4, 75))

    def test_permissions(self):
        self.client.force_login(make_user('sita@school.com', is_teacher=True))
        self.assertEqual(self.client.get(reverse('mark_attendance')).status_code, 200)
        self.client.force_login(make_user('aarav@school.com', is_student=True))
        self.assertEqual(self.client.get(reverse('mark_attendance')).status_code, 403)
        self.assertEqual(self.client.get(reverse('attendance_report')).status_code, 403)

    def test_seed_attendance_skips_saturdays_and_runs_twice(self):
        call_command('seed_attendance', days=5, stdout=StringIO())
        call_command('seed_attendance', days=5, stdout=StringIO())
        self.assertEqual(Attendance.objects.count(), 5 * Student.objects.count())
        self.assertFalse(Attendance.objects.filter(date__week_day=7).exists())  # 7 = Saturday
