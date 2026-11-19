from django.contrib import messages
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from academics.models import Subject
from home_auth.decorators import role_required
from school.utils import create_notification
from student.models import Student
from .forms import ExamForm
from .grading import grade_for
from .models import Exam, Mark


def exam_students(exam):
    """Every student of the exam's class, all sections together."""
    return Student.objects.filter(section__school_class=exam.school_class).select_related(
        'section'
    ).order_by('section__name', 'first_name', 'last_name')


def build_results(exam):
    """Turn the marks into a table: one row per student, one column per subject."""
    marks = exam.marks.select_related('subject')
    subjects = sorted({mark.subject for mark in marks}, key=lambda subject: subject.code)

    # {student_id: {subject_id: marks}}
    table = {}
    for mark in marks:
        table.setdefault(mark.student_id, {})[mark.subject_id] = mark.marks_obtained

    rows = []
    for student in exam_students(exam):
        scores = table.get(student.pk)
        if not scores:
            continue
        cells = [(scores.get(s.pk), scores.get(s.pk, 0) < exam.pass_marks) for s in subjects]
        total = sum(scores.values())
        percent = round(total * 100 / (exam.full_marks * len(subjects)), 2)
        rows.append({
            'student': student,
            'cells': cells,
            'total': total,
            'percent': percent,
            'grade': grade_for(percent),
            'passed': not any(failed for _, failed in cells),
        })

    rows.sort(key=lambda row: row['total'], reverse=True)
    for rank, row in enumerate(rows, start=1):
        row['rank'] = rank
    return subjects, rows


@role_required('admin', 'teacher')
def exam_list(request):
    exams = Exam.objects.select_related('school_class').annotate(
        mark_count=Count('marks')
    ).order_by('-start_date', 'school_class__order')  # Count() forgets Meta.ordering
    return render(request, 'exams/exams.html', {'exams': exams})


@role_required('admin')
def add_exam(request):
    form = ExamForm(request.POST or None)
    if form.is_valid():
        exam = form.save()
        create_notification(request.user, f'Added Exam: {exam}')
        messages.success(request, f'{exam} created. Now enter the marks.')
        return redirect('exam_list')
    context = {'form': form, 'title': 'Add Exam', 'back': 'exam_list'}
    return render(request, 'academics/form.html', context)


@role_required('admin', 'teacher')
def enter_marks(request, pk):
    exam = get_object_or_404(Exam.objects.select_related('school_class'), pk=pk)
    subjects = Subject.objects.all()
    subject_id = request.GET.get('subject', '')
    subject = subjects.filter(pk=subject_id).first() if subject_id.isdigit() else None
    context = {'exam': exam, 'subjects': subjects, 'subject': subject}
    if subject is None:
        return render(request, 'exams/marks.html', context)

    students = exam_students(exam)
    errors = {}
    if request.method == 'POST':
        for student in students:
            value = request.POST.get(f'marks_{student.pk}', '').strip()
            if value == '':
                continue  # left empty → not entered yet
            if not value.isdigit() or int(value) > exam.full_marks:
                errors[student.pk] = f'Enter 0 to {exam.full_marks}'
                continue
            Mark.objects.update_or_create(
                exam=exam,
                student=student,
                subject=subject,
                defaults={'marks_obtained': int(value)},
            )
        if not errors:
            messages.success(request, f'{subject.name} marks saved.')
            return redirect(f'{request.path}?subject={subject.pk}')
        messages.error(request, 'Some marks are wrong. Fix the red boxes and save again.')

    saved = dict(Mark.objects.filter(exam=exam, subject=subject).values_list('student_id', 'marks_obtained'))
    context['rows'] = [
        {
            'student': student,
            'value': request.POST.get(f'marks_{student.pk}', saved.get(student.pk, '')),
            'error': errors.get(student.pk),
        }
        for student in students
    ]
    return render(request, 'exams/marks.html', context)


@role_required('admin', 'teacher')
def exam_result(request, pk):
    exam = get_object_or_404(Exam.objects.select_related('school_class'), pk=pk)
    subjects, rows = build_results(exam)
    return render(request, 'exams/result.html', {'exam': exam, 'subjects': subjects, 'rows': rows})


@role_required('admin', 'teacher')
def report_card(request, pk, student_pk):
    exam = get_object_or_404(Exam.objects.select_related('school_class'), pk=pk)
    subjects, rows = build_results(exam)
    row = next((row for row in rows if row['student'].pk == student_pk), None)
    if row is None:
        raise Http404('No marks for this student in this exam.')

    lines = []
    for subject, (marks, failed) in zip(subjects, row['cells']):
        grade = grade_for(marks * 100 / exam.full_marks) if marks is not None else '—'
        lines.append({'subject': subject, 'marks': marks, 'grade': grade, 'failed': failed})

    days = row['student'].attendance.all()
    attendance = round(days.exclude(status='A').count() * 100 / days.count()) if days.exists() else None

    context = {'exam': exam, 'row': row, 'lines': lines, 'out_of': len(rows), 'attendance': attendance}
    return render(request, 'exams/report-card.html', context)
