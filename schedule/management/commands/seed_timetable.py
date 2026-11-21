import datetime

from django.core.management.base import BaseCommand

from academics.models import Subject
from classroom.models import Section
from schedule.models import Period

PERIODS_PER_DAY = 6
FIRST_BELL = datetime.datetime(2026, 1, 1, 10, 0)  # school starts at 10:00
LENGTH = datetime.timedelta(minutes=45)
BREAK = datetime.timedelta(minutes=30)  # tiffin break after the 3rd period


def period_times(number):
    start = FIRST_BELL + LENGTH * (number - 1) + (BREAK if number > 3 else datetime.timedelta())
    return start.time(), (start + LENGTH).time()


class Command(BaseCommand):
    help = 'Create a Sunday–Friday timetable (6 periods a day) for every section.'

    def handle(self, *args, **options):
        subjects = list(Subject.objects.prefetch_related('teachers'))
        if not subjects:
            self.stderr.write('No subjects yet. Run: python manage.py seed_academics')
            return

        busy = set(Period.objects.exclude(teacher=None).values_list('teacher_id', 'day', 'number'))
        for section_index, section in enumerate(Section.objects.all()):
            for day, _ in Period.Day.choices:
                for number in range(1, PERIODS_PER_DAY + 1):
                    if Period.objects.filter(section=section, day=day, number=number).exists():
                        continue
                    subject = subjects[(section_index + day + number) % len(subjects)]
                    # first teacher of this subject who is free in this period
                    teacher = next(
                        (t for t in subject.teachers.all() if (t.pk, day, number) not in busy), None
                    )
                    if teacher:
                        busy.add((teacher.pk, day, number))
                    start, end = period_times(number)
                    Period.objects.create(section=section, day=day, number=number, subject=subject,
                                          teacher=teacher, start_time=start, end_time=end)
        self.stdout.write(self.style.SUCCESS(f'Periods: {Period.objects.count()}'))
