from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from attendance.views import get_section
from classroom.models import Section
from home_auth.decorators import role_required
from school.utils import create_notification
from .forms import EventForm, PeriodForm
from .models import Event, Period


@role_required('admin', 'teacher')
def timetable(request):
    section = get_section(request)  # the same helper from Episode 6
    context = {
        'sections': Section.objects.select_related('school_class'),
        'section': section,
        'days': Period.Day.choices,
    }
    if section:
        periods = section.periods.select_related('subject', 'teacher')
        grid = {(period.day, period.number): period for period in periods}
        numbers = sorted({period.number for period in periods})
        context['rows'] = [
            {'number': number, 'cells': [grid.get((day, number)) for day, _ in Period.Day.choices]}
            for number in numbers
        ]
    return render(request, 'schedule/timetable.html', context)


@role_required('admin')
def add_period(request):
    form = PeriodForm(request.POST or None, initial={'section': request.GET.get('section')})
    if form.is_valid():
        period = form.save()
        messages.success(request, f'{period.subject.name} added to {period}.')
        return redirect(f"{reverse('timetable')}?section={period.section_id}")
    context = {'form': form, 'title': 'Add Period', 'back': 'timetable'}
    return render(request, 'academics/form.html', context)


@role_required('admin', 'teacher', 'student')
def event_list(request):
    today = timezone.localdate()
    # still running or still to come: its last day is today or later
    running_or_next = Q(end_date__gte=today) | Q(end_date__isnull=True, start_date__gte=today)
    context = {
        'upcoming': Event.objects.filter(running_or_next),
        'past': Event.objects.exclude(running_or_next).order_by('-start_date')[:5],
        'today': today,
    }
    return render(request, 'schedule/events.html', context)


@role_required('admin')
def add_event(request):
    form = EventForm(request.POST or None)
    if form.is_valid():
        event = form.save()
        create_notification(request.user, f'Added {event.get_kind_display()}: {event.title}')
        messages.success(request, f'{event.title} added.')
        return redirect('event_list')
    context = {'form': form, 'title': 'Add Holiday / Event', 'back': 'event_list'}
    return render(request, 'academics/form.html', context)
