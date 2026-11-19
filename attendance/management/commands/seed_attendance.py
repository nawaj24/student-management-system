import datetime
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from attendance.models import Attendance
from student.models import Student


class Command(BaseCommand):
    help = 'Create demo attendance for the last N school days (Saturdays are skipped).'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=20)

    def handle(self, *args, **options):
        rng = random.Random(7)
        students = list(Student.objects.all())
        records, day, school_days = [], timezone.localdate(), 0

        while school_days < options['days']:
            if day.weekday() != 5:  # 5 = Saturday, the weekly holiday in Nepal
                for student in students:
                    status = rng.choices(['P', 'L', 'A'], weights=[85, 5, 10])[0]
                    records.append(Attendance(student=student, date=day, status=status))
                school_days += 1
            day -= datetime.timedelta(days=1)

        # ignore_conflicts → rows that already exist are skipped, not duplicated
        Attendance.objects.bulk_create(records, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Attendance rows: {Attendance.objects.count()}'))
