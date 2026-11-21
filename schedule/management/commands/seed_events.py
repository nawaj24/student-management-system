import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from schedule.models import Event


class Command(BaseCommand):
    help = 'Create demo holidays and events around today.'

    def handle(self, *args, **options):
        today = timezone.localdate()
        day = lambda n: today + datetime.timedelta(days=n)
        christmas = datetime.date(today.year, 12, 25)
        events = [
            ('Annual Sports Day', Event.Kind.EVENT, day(6), day(7)),
            ('Parent-Teacher Meeting', Event.Kind.EVENT, day(13), None),
            ('Christmas', Event.Kind.HOLIDAY, christmas, None),
            ('Winter Vacation', Event.Kind.HOLIDAY, day(40), day(49)),
            ('Second Terminal Exam', Event.Kind.EXAM, day(55), day(61)),
            ('Science Exhibition', Event.Kind.EVENT, day(-12), None),
        ]
        for title, kind, start, end in events:
            Event.objects.get_or_create(
                title=title, defaults={'kind': kind, 'start_date': start, 'end_date': end}
            )
        self.stdout.write(self.style.SUCCESS(f'Events: {Event.objects.count()}'))
