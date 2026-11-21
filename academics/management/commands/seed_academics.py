from django.core.management.base import BaseCommand

from academics.models import Department, Subject
from teacher.models import Teacher

# department name, code, [subjects]
DEPARTMENTS = [
    ('Science', 'SCI', ['Science', 'Physics', 'Chemistry']),
    ('Mathematics', 'MTH', ['Mathematics']),
    ('Languages', 'LAN', ['English', 'Nepali']),
    ('Social & Computer', 'SOC', ['Social Studies', 'Computer']),
]


class Command(BaseCommand):
    help = 'Create demo departments and subjects, and link teachers to them.'

    def handle(self, *args, **options):
        for name, code, subject_names in DEPARTMENTS:
            department, _ = Department.objects.get_or_create(code=code, defaults={'name': name})
            for number, subject_name in enumerate(subject_names, start=1):
                subject, _ = Subject.objects.get_or_create(
                    code=f'{code}10{number}',
                    defaults={'name': subject_name, 'department': department},
                )
                # Teachers whose main subject matches teach this subject
                teachers = Teacher.objects.filter(subject=subject_name)
                subject.teachers.add(*teachers)
                if department.head is None and teachers:
                    department.head = teachers[0]
                    department.save()
        self.stdout.write(self.style.SUCCESS(
            f'Departments: {Department.objects.count()}, Subjects: {Subject.objects.count()}'
        ))
