from django.contrib import messages
from django.db.models import Count, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from home_auth.decorators import role_required
from school.utils import create_notification
from .forms import DepartmentForm, SubjectForm
from .models import Department, Subject


# ---------- Departments ----------

@role_required('admin', 'teacher')
def department_list(request):
    departments = Department.objects.select_related('head').annotate(
        subject_count=Count('subjects')
    )
    return render(request, 'academics/departments.html', {'departments': departments})


@role_required('admin', 'teacher')
def department_detail(request, slug):
    department = get_object_or_404(Department, slug=slug)
    subjects = department.subjects.prefetch_related('teachers')
    context = {'department': department, 'subjects': subjects}
    return render(request, 'academics/department-details.html', context)


@role_required('admin')
def add_department(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        department = form.save()
        create_notification(request.user, f'Added Department: {department.name}')
        messages.success(request, 'Department added successfully.')
        return redirect('department_list')
    context = {'form': form, 'title': 'Add Department', 'back': 'department_list'}
    return render(request, 'academics/form.html', context)


@role_required('admin')
def edit_department(request, slug):
    department = get_object_or_404(Department, slug=slug)
    form = DepartmentForm(request.POST or None, instance=department)
    if form.is_valid():
        form.save()
        messages.success(request, 'Department updated successfully.')
        return redirect('department_detail', slug=department.slug)
    context = {'form': form, 'title': 'Edit Department', 'back': 'department_list'}
    return render(request, 'academics/form.html', context)


@role_required('admin')
def delete_department(request, slug):
    department = get_object_or_404(Department, slug=slug)
    if request.method == 'POST':
        try:
            department.delete()
        except ProtectedError:
            messages.error(request, f'{department.name} still has subjects. Move or delete them first.')
        else:
            create_notification(request.user, f'Deleted Department: {department.name}')
            messages.success(request, 'Department deleted.')
    return redirect('department_list')


# ---------- Subjects ----------

@role_required('admin', 'teacher')
def subject_list(request):
    subjects = Subject.objects.select_related('department').prefetch_related('teachers')
    selected = request.GET.get('department', '')
    if selected:
        subjects = subjects.filter(department__slug=selected)
    context = {
        'subjects': subjects,
        'departments': Department.objects.all(),
        'selected': selected,
    }
    return render(request, 'academics/subjects.html', context)


@role_required('admin')
def add_subject(request):
    form = SubjectForm(request.POST or None)
    if form.is_valid():
        subject = form.save()
        create_notification(request.user, f'Added Subject: {subject.name}')
        messages.success(request, 'Subject added successfully.')
        return redirect('subject_list')
    context = {'form': form, 'title': 'Add Subject', 'back': 'subject_list'}
    return render(request, 'academics/form.html', context)


@role_required('admin')
def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(request.POST or None, instance=subject)
    if form.is_valid():
        form.save()
        messages.success(request, 'Subject updated successfully.')
        return redirect('subject_list')
    context = {'form': form, 'title': 'Edit Subject', 'back': 'subject_list'}
    return render(request, 'academics/form.html', context)


@role_required('admin')
def delete_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        create_notification(request.user, f'Deleted Subject: {subject.name}')
        subject.delete()
        messages.success(request, 'Subject deleted.')
    return redirect('subject_list')
