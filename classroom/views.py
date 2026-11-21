from django.contrib import messages
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from home_auth.decorators import role_required
from school.utils import create_notification
from .forms import SchoolClassForm, SectionForm
from .models import SchoolClass, Section


@role_required('admin', 'teacher')
def class_list(request):
    sections = Section.objects.select_related('class_teacher').annotate(
        student_count=Count('students')
    ).order_by('name')
    classes = SchoolClass.objects.prefetch_related(Prefetch('sections', queryset=sections))
    return render(request, 'classroom/classes.html', {'classes': classes})


@role_required('admin', 'teacher')
def section_detail(request, pk):
    section = get_object_or_404(Section.objects.select_related('school_class', 'class_teacher'), pk=pk)
    students = section.students.order_by('first_name', 'last_name')
    return render(request, 'classroom/section-details.html', {'section': section, 'students': students})


@role_required('admin')
def add_class(request):
    form = SchoolClassForm(request.POST or None)
    if form.is_valid():
        school_class = form.save()
        create_notification(request.user, f'Added Class: {school_class.name}')
        messages.success(request, f'{school_class.name} added. Now add its sections.')
        return redirect('class_list')
    context = {'form': form, 'title': 'Add Class', 'back': 'class_list'}
    return render(request, 'academics/form.html', context)


@role_required('admin')
def add_section(request):
    form = SectionForm(request.POST or None, initial={'school_class': request.GET.get('school_class')})
    if form.is_valid():
        section = form.save()
        create_notification(request.user, f'Added Section: {section}')
        messages.success(request, f'Section {section} added.')
        return redirect('class_list')
    context = {'form': form, 'title': 'Add Section', 'back': 'class_list'}
    return render(request, 'academics/form.html', context)


@role_required('admin')
def edit_section(request, pk):
    section = get_object_or_404(Section, pk=pk)
    form = SectionForm(request.POST or None, instance=section)
    if form.is_valid():
        form.save()
        messages.success(request, f'Section {section} updated.')
        return redirect('section_detail', pk=section.pk)
    context = {'form': form, 'title': 'Edit Section', 'back': 'class_list'}
    return render(request, 'academics/form.html', context)
