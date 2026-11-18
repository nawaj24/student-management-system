import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from teacher.models import Teacher

TEACHERS = [
    ('Ramesh', 'Yadav', 'Male', 'Mathematics'), ('Sunita', 'Jha', 'Female', 'English'),
    ('Bikash', 'Sah', 'Male', 'Science'), ('Anita', 'Mishra', 'Female', 'Nepali'),
    ('Rajan', 'Thakur', 'Male', 'Computer'), ('Pooja', 'Gupta', 'Female', 'Social Studies'),
    ('Dinesh', 'Karna', 'Male', 'Physics'), ('Kalpana', 'Mandal', 'Female', 'Chemistry'),
]


class Command(BaseCommand):
    help = 'Create demo teachers.'

    def handle(self, *args, **options):
        rng = random.Random(7)
        today = timezone.localdate()
        created = 0
        for n, (first, last, gender, subject) in enumerate(TEACHERS, start=1):
            _, is_new = Teacher.objects.get_or_create(
                teacher_id=f'T{n:03d}',
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'gender': gender,
                    'date_of_birth': date(rng.randint(1975, 1995), rng.randint(1, 12), 15),
                    'mobile_number': '98' + str(rng.randint(10000000, 99999999)),
                    'email': f'{first.lower()}.{last.lower()}@school.com',
                    'qualification': rng.choice(['B.Ed', 'M.Ed', 'M.Sc', 'M.A']),
                    'subject': subject,
                    'joining_date': today - timedelta(days=rng.randint(30, 2000)),
                    'address': 'Janakpur, Dhanusha',
                },
            )
            created += is_new
        total = Teacher.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Created {created} teachers (total: {total})'))
