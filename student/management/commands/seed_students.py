import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from student.models import Parent, Student

FIRST_BOYS = ['Aarav', 'Rohan', 'Sagar', 'Bibek', 'Nabin', 'Suraj', 'Aayush', 'Kiran', 'Rajesh', 'Anish', 'Prakash', 'Sandeep']
FIRST_GIRLS = ['Sita', 'Anjali', 'Priya', 'Puja', 'Sunita', 'Nisha', 'Kritika', 'Asmita', 'Rekha', 'Sabina', 'Manisha', 'Shristi']
LAST = ['Yadav', 'Sah', 'Jha', 'Mandal', 'Thakur', 'Mishra', 'Karna', 'Shrestha', 'Gupta', 'Ansari', 'Chaudhary', 'Singh']


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
            first = rng.choice(FIRST_BOYS if gender == 'Male' else FIRST_GIRLS)
            last = rng.choice(LAST)
            student_class = str(rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 9, 8]))
            parent = Parent.objects.create(
                father_name=f'{rng.choice(FIRST_BOYS)} {last}', father_mobile='98' + str(rng.randint(10000000, 99999999)),
                father_email=f'father{n}@example.com', mother_name=f'{rng.choice(FIRST_GIRLS)} {last}',
                mother_mobile='98' + str(rng.randint(10000000, 99999999)), mother_email=f'mother{n}@example.com',
                present_address='Janakpur, Dhanusha', permanent_address='Janakpur, Dhanusha',
            )
            Student.objects.create(
                first_name=first, last_name=last, student_id=f'S{n:04d}', gender=gender,
                date_of_birth=date(2008 + rng.randint(0, 10), rng.randint(1, 12), rng.randint(1, 28)),
                student_class=student_class, religion=rng.choice(['Hindu', 'Muslim', 'Buddhist', 'Christian']),
                joining_date=today - timedelta(days=rng.randint(0, 400)),
                mobile_number='98' + str(rng.randint(10000000, 99999999)), admission_number=f'A{n:04d}',
                section=rng.choice(['A', 'B']), parent=parent,
            )
        self.stdout.write(self.style.SUCCESS(f"Created {options['count']} students (total: {Student.objects.count()})"))
