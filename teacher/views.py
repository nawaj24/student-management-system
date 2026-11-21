from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from home_auth.decorators import role_required
from school.utils import create_notification
from .forms import TeacherForm
from .models import Teacher


@role_required('admin', 'teacher')
def teacher_list(request):
    query = request.GET.get('q', '').strip()
    teachers = Teacher.objects.all()
    if query:
        teachers = teachers.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(teacher_id__icontains=query)
            | Q(subject__icontains=query)
        )
    return render(request, 'teachers/teachers.html', {'teachers': teachers, 'query': query})


@role_required('admin', 'teacher')
def teacher_detail(request, slug):
    teacher = get_object_or_404(Teacher, slug=slug)
    return render(request, 'teachers/teacher-details.html', {'teacher': teacher})


@role_required('admin')
def add_teacher(request):
    form = TeacherForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        teacher = form.save()
        create_notification(request.user, f'Added Teacher: {teacher.full_name}')
        messages.success(request, 'Teacher added successfully.')
        return redirect('teacher_list')
    return render(request, 'teachers/teacher-form.html', {'form': form, 'title': 'Add Teacher'})


@role_required('admin')
def edit_teacher(request, slug):
    teacher = get_object_or_404(Teacher, slug=slug)
    form = TeacherForm(request.POST or None, request.FILES or None, instance=teacher)
    if form.is_valid():
        form.save()
        create_notification(request.user, f'Updated Teacher: {teacher.full_name}')
        messages.success(request, 'Teacher updated successfully.')
        return redirect('teacher_detail', slug=teacher.slug)
    return render(request, 'teachers/teacher-form.html', {'form': form, 'title': 'Edit Teacher'})


@role_required('admin')
def delete_teacher(request, slug):
    teacher = get_object_or_404(Teacher, slug=slug)
    if request.method == 'POST':
        create_notification(request.user, f'Deleted Teacher: {teacher.full_name}')
        teacher.delete()
        messages.success(request, 'Teacher deleted.')
    return redirect('teacher_list')
