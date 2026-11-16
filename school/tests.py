from django.test import TestCase
from django.urls import reverse

from home_auth.models import CustomUser, PasswordResetRequest
from school.models import Notification
from student.models import Student


STUDENT_FORM = {
    'first_name': 'Ram', 'last_name': 'Sharma', 'student_id': 'S001', 'gender': 'Male',
    'date_of_birth': '2010-05-01', 'student_class': '10', 'religion': 'Hindu',
    'joining_date': '2024-04-01', 'mobile_number': '9800000000', 'admission_number': 'A001',
    'section': 'A', 'father_name': 'Hari', 'father_occupation': 'Farmer',
    'father_mobile': '9800000001', 'father_email': 'hari@example.com', 'mother_name': 'Sita',
    'mother_occupation': 'Teacher', 'mother_mobile': '9800000002',
    'mother_email': 'sita@example.com', 'present_address': 'Janakpur',
    'permanent_address': 'Janakpur',
}


class AuthFlowTests(TestCase):
    def test_signup_with_role_then_login_redirects_to_dashboard(self):
        response = self.client.post(reverse('signup'), {
            'first_name': 'Sita', 'last_name': 'Devi', 'email': 'sita@school.com',
            'password': 'StrongPass123', 'confirm_password': 'StrongPass123', 'role': 'teacher',
        })
        self.assertRedirects(response, reverse('teacher_dashboard'))
        self.client.logout()
        response = self.client.post(reverse('login'), {'email': 'sita@school.com', 'password': 'StrongPass123'})
        self.assertRedirects(response, reverse('teacher_dashboard'))

    def test_signup_cannot_create_admin(self):
        self.client.post(reverse('signup'), {
            'first_name': 'X', 'last_name': 'Y', 'email': 'x@school.com',
            'password': 'StrongPass123', 'confirm_password': 'StrongPass123', 'role': 'admin',
        })
        self.assertFalse(CustomUser.objects.filter(email='x@school.com').exists())

    def test_superuser_login_goes_to_admin_dashboard(self):
        CustomUser.objects.create_superuser(username='admin@school.com', email='admin@school.com', password='StrongPass123')
        response = self.client.post(reverse('login'), {'email': 'admin@school.com', 'password': 'StrongPass123'})
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_password_reset_link_works_once(self):
        user = CustomUser.objects.create_user(username='s@school.com', email='s@school.com', password='OldPass12345')
        self.client.post(reverse('forgot-password'), {'email': 's@school.com'})
        token = PasswordResetRequest.objects.get(user=user).token
        response = self.client.post(reverse('reset-password', args=[token]), {'new_password': 'NewPass12345'})
        self.assertRedirects(response, reverse('login'))
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewPass12345'))
        self.assertFalse(PasswordResetRequest.objects.filter(token=token).exists())

    def test_pages_need_login(self):
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)


class StudentAndNotificationTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(username='admin@school.com', email='admin@school.com', password='StrongPass123')
        self.client.force_login(self.admin)

    def test_add_view_edit_delete_student_and_notifications(self):
        # a student can be added without a photo
        response = self.client.post(reverse('add_student'), STUDENT_FORM)
        self.assertRedirects(response, reverse('student_list'))
        student = Student.objects.get(student_id='S001')

        self.assertEqual(self.client.get(reverse('student_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('view_student', args=[student.slug])).status_code, 200)
        self.assertEqual(self.client.get(reverse('edit_student', args=[student.slug])).status_code, 200)

        edited = dict(STUDENT_FORM, first_name='Shyam')
        self.client.post(reverse('edit_student', args=[student.slug]), edited)
        student.refresh_from_db()
        self.assertEqual(student.first_name, 'Shyam')

        page = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(page.context['unread_notification_count'], 2)

        self.client.post(reverse('mark_notifications_as_read'))
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 0)

        self.client.post(reverse('delete_student', args=[student.slug]))
        self.assertFalse(Student.objects.exists())
        self.client.post(reverse('clear_all_notifications'))
        self.assertEqual(Notification.objects.count(), 0)

    def test_all_dashboards_render(self):
        for name in ('admin_dashboard', 'teacher_dashboard', 'dashboard'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
