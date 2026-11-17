from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect

from home_auth.decorators import role_required
from .dashboard import get_dashboard_stats

from .models import Notification


DASHBOARDS = {
    'admin': 'admin_dashboard',
    'teacher': 'teacher_dashboard',
    'student': 'dashboard',
}


def get_dashboard_url(user):
    """Return the dashboard URL name for the user's role."""
    return DASHBOARDS.get(user.role)


def index(request):
    if request.user.is_authenticated and get_dashboard_url(request.user):
        return redirect(get_dashboard_url(request.user))
    return redirect('login')


@role_required('student')
def dashboard(request):
    return render(request, "students/student-dashboard.html")


@role_required('admin')
def admin_dashboard(request):
    return render(request, "Home/index.html", get_dashboard_stats())


@role_required('teacher')
def teacher_dashboard(request):
    return render(request, "Home/index.html", get_dashboard_stats())


@login_required
def mark_notification_as_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return HttpResponseForbidden()


@login_required
def clear_all_notification(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'success'})
    return HttpResponseForbidden()
