from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, PasswordResetRequest
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from school.views import get_dashboard_url


def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')  # student or teacher (admin is created with createsuperuser)

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/register.html')

        if role not in ('student', 'teacher'):
            messages.error(request, 'Please select a valid role.')
            return render(request, 'authentication/register.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'authentication/register.html')

        # Create the user
        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        # Assign the selected role
        if role == 'student':
            user.is_student = True
        elif role == 'teacher':
            user.is_teacher = True
        user.save()

        login(request, user)
        messages.success(request, 'Signup successful!')
        return redirect(get_dashboard_url(user))
    return render(request, 'authentication/register.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            
            # Redirect user based on their role (superuser counts as admin)
            dashboard_url = get_dashboard_url(user)
            if dashboard_url:
                return redirect(dashboard_url)
            logout(request)
            messages.error(request, 'Invalid user role')
            return redirect('login')

        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'authentication/login.html')  # Render login template


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = CustomUser.objects.filter(email=email).first()
        
        if user:
            reset_request = PasswordResetRequest.objects.create(user=user, email=email)
            reset_request.send_reset_email()
            messages.success(request, 'Reset link sent to your email.')
        else:
            messages.error(request, 'Email not found.')
    
    return render(request, 'authentication/forgot-password.html')  # Render forgot password template


def reset_password_view(request, token):
    reset_request = PasswordResetRequest.objects.filter(token=token).first()
    
    if not reset_request or not reset_request.is_valid():
        messages.error(request, 'Invalid or expired reset link')
        return redirect('forgot-password')

    if request.method == 'POST':
        new_password = request.POST['new_password']
        reset_request.user.set_password(new_password)
        reset_request.user.save()
        reset_request.delete()  # a reset link works only once
        messages.success(request, 'Password reset successful')
        return redirect('login')

    return render(request, 'authentication/reset_password.html', {'token': token})  # Render reset password template


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')
