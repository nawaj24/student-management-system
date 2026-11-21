import datetime

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone

from classroom.models import Section
from home_auth.decorators import role_required
from .models import Attendance


def get_section(request):
    """?section=8 in the URL → that Section, or None."""
    section_id = request.GET.get('section', '')
    if not section_id.isdigit():
        return None
    return Section.objects.select_related('school_class').filter(pk=section_id).first()


def get_date(request):
    """?date=2026-11-19 in the URL → a date. Missing or wrong → today."""
    try:
        return datetime.date.fromisoformat(request.GET.get('date', ''))
    except ValueError:
        return timezone.localdate()


@role_required('admin', 'teacher')
def mark_attendance(request):
    section, day = get_section(request), get_date(request)
    context = {
        'sections': Section.objects.select_related('school_class'),
        'section': section,
        'day': day,
        'statuses': Attendance.Status.choices,
    }
    if section is None:
        return render(request, 'attendance/mark.html', context)

    students = section.students.order_by('first_name', 'last_name')

    if request.method == 'POST':
        if day > timezone.localdate():
            messages.error(request, 'You cannot mark attendance for a future date.')
        else:
            for student in students:
                status = request.POST.get(f'status_{student.pk}')
                if status not in Attendance.Status.values:
                    status = Attendance.Status.PRESENT
                Attendance.objects.update_or_create(
                    student=student,
                    date=day,
                    defaults={'status': status, 'marked_by': request.user},
                )
            messages.success(request, f'Attendance saved for {section} on {day:%d %b %Y}.')
        return redirect(f'{request.path}?section={section.pk}&date={day}')

    saved = dict(
        Attendance.objects.filter(student__in=students, date=day).values_list('student_id', 'status')
    )
    context['rows'] = [(student, saved.get(student.pk, Attendance.Status.PRESENT)) for student in students]
    context['already_marked'] = bool(saved)
    return render(request, 'attendance/mark.html', context)


@role_required('admin', 'teacher')
def attendance_report(request):
    section = get_section(request)
    month = request.GET.get('month', '')
    try:
        year, month_number = (int(part) for part in month.split('-'))
    except ValueError:
        today = timezone.localdate()
        year, month_number = today.year, today.month

    rows = []
    if section:
        in_month = Q(attendance__date__year=year, attendance__date__month=month_number)
        students = section.students.annotate(
            present=Count('attendance', filter=in_month & Q(attendance__status='P')),
            late=Count('attendance', filter=in_month & Q(attendance__status='L')),
            absent=Count('attendance', filter=in_month & Q(attendance__status='A')),
        ).order_by('first_name', 'last_name')
        for student in students:
            total = student.present + student.late + student.absent
            percent = round((student.present + student.late) * 100 / total) if total else None
            rows.append({'student': student, 'total': total, 'percent': percent})

    context = {
        'sections': Section.objects.select_related('school_class'),
        'section': section,
        'month': f'{year}-{month_number:02d}',
        'rows': rows,
    }
    return render(request, 'attendance/report.html', context)
