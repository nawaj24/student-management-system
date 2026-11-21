import datetime
import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from classroom.models import SchoolClass
from fees.models import FeeStructure, Payment


class Command(BaseCommand):
    help = 'Create demo fees for every class and some payments (full, partial or none).'

    def handle(self, *args, **options):
        rng = random.Random(5)
        today = timezone.localdate()
        for school_class in SchoolClass.objects.all():
            tuition = Decimal(1500 + school_class.order * 100)
            for title, amount, days in [
                ('Admission Fee', Decimal(5000), -60),
                ('Tuition · Kartik', tuition, -25),
                ('Tuition · Mangsir', tuition, 5),
            ]:
                fee, created = FeeStructure.objects.get_or_create(
                    school_class=school_class, title=title,
                    defaults={'amount': amount, 'due_date': today + datetime.timedelta(days=days)},
                )
                if not created:
                    continue  # payments were made the first time
                for section in school_class.sections.all():
                    for student in section.students.all():
                        choice = rng.random()
                        if choice < 0.6:
                            paid = fee.amount  # full
                        elif choice < 0.8:
                            paid = (fee.amount / 2).quantize(Decimal('1'))  # half
                        else:
                            continue  # not paid yet
                        Payment.objects.create(student=student, fee=fee, amount=paid,
                                               method=rng.choice(Payment.Method.values))
        self.stdout.write(self.style.SUCCESS(
            f'Fees: {FeeStructure.objects.count()}, Payments: {Payment.objects.count()}'
        ))
