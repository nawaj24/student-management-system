from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect

from .models import Notification


def get_dashboard_url(user):
    """Return the dashboard URL name for the user's role."""
    if user.is_superuser or user.is_admin:
        return 'admin_dashboard'
    if user.is_teacher:
        return 'teacher_dashboard'
    if user.is_student:
        return 'dashboard'
    return None


def index(request):
    if request.user.is_authenticated and get_dashboard_url(request.user):
        return redirect(get_dashboard_url(request.user))
    return redirect('login')


@login_required
def dashboard(request):
    return render(request, "students/student-dashboard.html")


@login_required
def admin_dashboard(request):
    # Full admin dashboard is built in Episode 2
    return render(request, "Home/index.html")


@login_required
def teacher_dashboard(request):
    # Full teacher dashboard is built in Episode 2
    return render(request, "Home/index.html")


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
