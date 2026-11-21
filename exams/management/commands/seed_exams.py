import datetime
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from academics.models import Subject
from classroom.models import SchoolClass
from exams.models import Exam, Mark

SUBJECTS = ['English', 'Nepali', 'Mathematics', 'Science']


class Command(BaseCommand):
    help = 'Create a "First Terminal" exam for every class, with demo marks.'

    def handle(self, *args, **options):
        subjects = list(Subject.objects.filter(name__in=SUBJECTS))
        if not subjects:
            self.stderr.write('No subjects yet. Run: python manage.py seed_academics')
            return

        rng = random.Random(11)
        start = timezone.localdate() - datetime.timedelta(days=30)
        marks = []
        for school_class in SchoolClass.objects.all():
            exam, _ = Exam.objects.get_or_create(
                name='First Terminal', school_class=school_class, defaults={'start_date': start}
            )
            for section in school_class.sections.all():
                for student in section.students.all():
                    for subject in subjects:
                        score = max(15, min(100, round(rng.gauss(68, 15))))
                        marks.append(Mark(exam=exam, student=student, subject=subject, marks_obtained=score))

        Mark.objects.bulk_create(marks, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(
            f'Exams: {Exam.objects.count()}, Marks: {Mark.objects.count()}'
        ))
