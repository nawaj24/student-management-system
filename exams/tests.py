import datetime
from io import StringIO

from django.core.management import call_command
from django.db.models import Count
from django.test import TestCase
from django.urls import reverse

from academics.models import Subject
from classroom.models import SchoolClass
from home_auth.models import CustomUser
from school.tests import make_user
from .grading import grade_for
from .models import Exam, Mark
from .views import exam_students


class ExamTests(TestCase):
    """Exams and results (Episode 7)."""

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='admin@school.com', email='admin@school.com', password='StrongPass123')
        self.client.force_login(self.admin)
        for name in ['seed_classes', 'seed_teachers', 'seed_academics']:
            call_command(name, stdout=StringIO())
        call_command('seed_students', count=30, stdout=StringIO())
        biggest = SchoolClass.objects.annotate(n=Count('sections__students')).order_by('-n').first()
        self.exam = Exam.objects.create(name='First Terminal', school_class=biggest,
                                        start_date=datetime.date(2026, 10, 1))
        self.students = list(exam_students(self.exam))
        self.maths = Subject.objects.get(name='Mathematics')
        self.url = f"{reverse('enter_marks', args=[self.exam.pk])}?subject={self.maths.pk}"

    def test_grade_scale(self):
        self.assertEqual([grade_for(p) for p in (95, 90, 75, 50, 40, 35, 20)],
                         ['A+', 'A+', 'B+', 'C+', 'C', 'D', 'NG'])

    def test_enter_marks_and_update(self):
        first = self.students[0]
        self.client.post(self.url, {f'marks_{first.pk}': '55'})
        self.client.post(self.url, {f'marks_{first.pk}': '72'})
        self.assertEqual(Mark.objects.get(student=first).marks_obtained, 72)
        self.assertEqual(Mark.objects.count(), 1)  # empty boxes are skipped

    def test_wrong_marks_are_not_saved(self):
        response = self.client.post(self.url, {f'marks_{self.students[0].pk}': '120'})
        self.assertContains(response, 'Enter 0 to 100')
        self.assertFalse(Mark.objects.exists())

    def test_result_rank_percent_and_fail(self):
        a, b = self.students[:2]
        english = Subject.objects.get(name='English')
        for student, maths, eng in [(a, 90, 80), (b, 95, 30)]:
            Mark.objects.create(exam=self.exam, student=student, subject=self.maths, marks_obtained=maths)
            Mark.objects.create(exam=self.exam, student=student, subject=english, marks_obtained=eng)
        response = self.client.get(reverse('exam_result', args=[self.exam.pk]))
        first, second = response.context['rows']
        self.assertEqual((first['student'], first['rank'], first['percent'], first['grade']), (a, 1, 85.0, 'A'))
        self.assertFalse(second['passed'])  # 30 in English is below 40

    def test_report_card(self):
        student = self.students[0]
        Mark.objects.create(exam=self.exam, student=student, subject=self.maths, marks_obtained=64)
        response = self.client.get(reverse('report_card', args=[self.exam.pk, student.pk]))
        self.assertContains(response, 'PASS')
        self.assertContains(response, '64.0%')
        missing = self.client.get(reverse('report_card', args=[self.exam.pk, self.students[1].pk]))
        self.assertEqual(missing.status_code, 404)

    def test_permissions(self):
        self.client.force_login(make_user('sita@school.com', is_teacher=True))
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertEqual(self.client.get(reverse('add_exam')).status_code, 403)
        self.client.force_login(make_user('aarav@school.com', is_student=True))
        self.assertEqual(self.client.get(reverse('exam_list')).status_code, 403)

    def test_seed_exams(self):
        call_command('seed_exams', stdout=StringIO())
        call_command('seed_exams', stdout=StringIO())
        self.assertEqual(Exam.objects.filter(name='First Terminal').count(), 10)
        self.assertEqual(Mark.objects.count(), 30 * 4)
