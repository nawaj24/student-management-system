import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from student.models import Parent, Student

BOYS = ['Aarav', 'Rohan', 'Sagar', 'Bibek', 'Nabin', 'Suraj', 'Kiran', 'Anish']
GIRLS = ['Sita', 'Anjali', 'Priya', 'Puja', 'Sunita', 'Nisha', 'Kritika', 'Rekha']
SURNAMES = ['Yadav', 'Sah', 'Jha', 'Mandal', 'Thakur', 'Mishra', 'Karna', 'Gupta']
CLASSES = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']


def random_mobile(rng):
    return '98' + str(rng.randint(10000000, 99999999))


class Command(BaseCommand):
    help = 'Create demo students so the dashboards have data to show.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=60)

    def handle(self, *args, **options):
        rng = random.Random(42)  # same data every time
        today = timezone.localdate()
        start = Student.objects.count()

        for n in range(start + 1, start + options['count'] + 1):
            gender = rng.choice(['Male', 'Female'])
            first_name = rng.choice(BOYS if gender == 'Male' else GIRLS)
            last_name = rng.choice(SURNAMES)

            parent = Parent.objects.create(
                father_name=f'{rng.choice(BOYS)} {last_name}',
                father_mobile=random_mobile(rng),
                father_email=f'father{n}@example.com',
                mother_name=f'{rng.choice(GIRLS)} {last_name}',
                mother_mobile=random_mobile(rng),
                mother_email=f'mother{n}@example.com',
                present_address='Janakpur, Dhanusha',
                permanent_address='Janakpur, Dhanusha',
            )

            Student.objects.create(
                first_name=first_name,
                last_name=last_name,
                student_id=f'S{n:04d}',
                gender=gender,
                date_of_birth=date(rng.randint(2008, 2018), rng.randint(1, 12), rng.randint(1, 28)),
                student_class=rng.choice(CLASSES),
                religion=rng.choice(['Hindu', 'Muslim', 'Buddhist', 'Christian']),
                joining_date=today - timedelta(days=rng.randint(0, 400)),
                mobile_number=random_mobile(rng),
                admission_number=f'A{n:04d}',
                section=rng.choice(['A', 'B']),
                parent=parent,
            )

        total = Student.objects.count()
        message = f"Created {options['count']} students (total: {total})"
        self.stdout.write(self.style.SUCCESS(message))
