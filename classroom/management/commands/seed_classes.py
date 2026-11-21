from django.core.management.base import BaseCommand

from classroom.models import SchoolClass, Section


class Command(BaseCommand):
    help = 'Create Class 1 to Class 10, each with sections A and B.'

    def handle(self, *args, **options):
        for number in range(1, 11):
            school_class, _ = SchoolClass.objects.get_or_create(
                name=f'Class {number}', defaults={'order': number}
            )
            for name in ['A', 'B']:
                Section.objects.get_or_create(school_class=school_class, name=name)
        self.stdout.write(self.style.SUCCESS(
            f'Classes: {SchoolClass.objects.count()}, Sections: {Section.objects.count()}'
        ))
