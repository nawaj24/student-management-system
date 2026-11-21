import datetime
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from academics.models import Subject
from classroom.models import Section
from home_auth.models import CustomUser
from school.tests import make_user
from .models import Event, Period


class ScheduleTests(TestCase):
    """Timetable, holidays and events (Episode 9)."""

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='admin@school.com', email='admin@school.com', password='StrongPass123')
        self.client.force_login(self.admin)
        for name in ['seed_classes', 'seed_teachers', 'seed_academics']:
            call_command(name, stdout=StringIO())
        self.a, self.b = Section.objects.all()[:2]
        self.maths = Subject.objects.get(name='Mathematics')
        self.teacher = self.maths.teachers.first()

    def period_data(self, section, **extra):
        data = {'section': section.pk, 'day': 0, 'number': 1, 'subject': self.maths.pk,
                'teacher': self.teacher.pk, 'start_time': '10:00', 'end_time': '10:45'}
        data.update(extra)
        return data

    def test_add_period_and_grid(self):
        self.client.post(reverse('add_period'), self.period_data(self.a))
        response = self.client.get(reverse('timetable'), {'section': self.a.pk})
        row = response.context['rows'][0]
        self.assertEqual(row['number'], 1)
        self.assertEqual(row['cells'][0].subject, self.maths)  # Sunday
        self.assertIsNone(row['cells'][1])  # Monday is empty

    def test_teacher_cannot_be_in_two_classes_at_once(self):
        self.client.post(reverse('add_period'), self.period_data(self.a))
        response = self.client.post(reverse('add_period'), self.period_data(self.b))
        self.assertContains(response, 'already has a class in this period')
        self.assertEqual(Period.objects.count(), 1)

    def test_end_time_after_start_time(self):
        response = self.client.post(reverse('add_period'), self.period_data(self.a, end_time='09:00'))
        self.assertContains(response, 'End time must be after the start time')

    def test_events_upcoming_and_past(self):
        today = timezone.localdate()
        Event.objects.create(title='Sports Day', start_date=today + datetime.timedelta(days=3))
        Event.objects.create(title='Old Fair', start_date=today - datetime.timedelta(days=3))
        Event.objects.create(title='Vacation', kind='holiday', start_date=today - datetime.timedelta(days=1),
                             end_date=today + datetime.timedelta(days=2))
        response = self.client.get(reverse('event_list'))
        self.assertEqual([e.title for e in response.context['upcoming']], ['Vacation', 'Sports Day'])
        self.assertEqual([e.title for e in response.context['past']], ['Old Fair'])

    def test_permissions(self):
        self.client.force_login(make_user('aarav@school.com', is_student=True))
        self.assertEqual(self.client.get(reverse('event_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('timetable')).status_code, 403)
        self.assertEqual(self.client.get(reverse('add_event')).status_code, 403)

    def test_seed_timetable_has_no_teacher_clash(self):
        call_command('seed_timetable', stdout=StringIO())
        call_command('seed_timetable', stdout=StringIO())
        self.assertEqual(Period.objects.count(), Section.objects.count() * 6 * 6)
        call_command('seed_events', stdout=StringIO())
        self.assertEqual(Event.objects.count(), 6)
