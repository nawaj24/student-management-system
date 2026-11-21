from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from home_auth.decorators import role_required
from school.utils import create_notification
from student.models import Student
from .forms import FeeStructureForm, PaymentForm
from .models import FeeStructure, Payment


@role_required('admin')
def fee_list(request):
    fees = FeeStructure.objects.select_related('school_class').annotate(
        collected=Sum('payments__amount', default=0)
    ).order_by('due_date', 'school_class__order')
    return render(request, 'fees/fees.html', {'fees': fees})


@role_required('admin')
def add_fee(request):
    form = FeeStructureForm(request.POST or None)
    if form.is_valid():
        fee = form.save()
        create_notification(request.user, f'Added Fee: {fee.title} for {fee.school_class}')
        messages.success(request, 'Fee added.')
        return redirect('fee_list')
    context = {'form': form, 'title': 'Add Fee', 'back': 'fee_list'}
    return render(request, 'academics/form.html', context)


def fee_lines(student):
    """Every fee of the student's class with paid, balance and status."""
    today = timezone.localdate()
    fees = FeeStructure.objects.filter(school_class=student.section.school_class).annotate(
        paid=Sum('payments__amount', filter=Q(payments__student=student), default=0)
    )
    lines = []
    for fee in fees:
        balance = fee.amount - fee.paid
        if balance <= 0:
            status = 'Paid'
        elif fee.paid > 0:
            status = 'Partial'
        elif fee.due_date < today:
            status = 'Overdue'
        else:
            status = 'Unpaid'
        lines.append({'fee': fee, 'paid': fee.paid, 'balance': balance, 'status': status})
    return lines


@role_required('admin')
def student_fees(request, slug):
    student = get_object_or_404(Student.objects.select_related('section__school_class'), slug=slug)
    if student.section is None:
        messages.error(request, 'Put this student in a section first.')
        return redirect('view_student', slug=slug)

    form = PaymentForm(request.POST or None, student=student)
    if form.is_valid():
        payment = form.save(commit=False)
        payment.student = student
        payment.received_by = request.user
        payment.save()
        messages.success(request, f'Rs. {payment.amount} received. Receipt {payment.receipt_number}.')
        return redirect('fee_receipt', pk=payment.pk)

    lines = fee_lines(student)
    context = {
        'student': student,
        'lines': lines,
        'total_due': sum(line['balance'] for line in lines),
        'payments': student.payments.select_related('fee'),
        'form': form,
    }
    return render(request, 'fees/student-fees.html', context)


@role_required('admin')
def fee_receipt(request, pk):
    payment = get_object_or_404(Payment.objects.select_related('student', 'fee', 'received_by'), pk=pk)
    return render(request, 'fees/receipt.html', {'payment': payment})


@role_required('admin')
def pending_dues(request):
    # Total fees of each class: {class_id: amount}
    class_totals = dict(
        FeeStructure.objects.values_list('school_class').annotate(total=Sum('amount'))
    )
    students = Student.objects.filter(section__isnull=False).select_related(
        'section__school_class'
    ).annotate(paid=Sum('payments__amount', default=0))

    rows = []
    for student in students:
        total = class_totals.get(student.section.school_class_id, 0)
        due = total - student.paid
        if due > 0:
            rows.append({'student': student, 'total': total, 'paid': student.paid, 'due': due})
    rows.sort(key=lambda row: row['due'], reverse=True)

    context = {'rows': rows, 'grand_total': sum(row['due'] for row in rows)}
    return render(request, 'fees/dues.html', context)
