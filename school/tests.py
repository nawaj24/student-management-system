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

    def test_admin_dashboard_renders(self):
        self.assertEqual(self.client.get(reverse('admin_dashboard')).status_code, 200)


def make_user(email, **roles):
    user = CustomUser.objects.create_user(username=email, email=email, password='StrongPass123')
    for role, value in roles.items():
        setattr(user, role, value)
    user.save()
    return user


class RoleAccessTests(TestCase):
    """Each role can open only its own pages (Episode 1)."""

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(username='admin@school.com', email='admin@school.com', password='StrongPass123')
        self.teacher = make_user('teacher@school.com', is_teacher=True)
        self.student = make_user('student@school.com', is_student=True)

    def status(self, user, name, *args):
        self.client.force_login(user)
        return self.client.get(reverse(name, args=args)).status_code

    def test_role_property(self):
        self.assertEqual(self.admin.role, 'admin')
        self.assertEqual(self.teacher.role, 'teacher')
        self.assertEqual(self.student.role, 'student')

    def test_each_role_opens_only_its_dashboard(self):
        expected = {
            self.admin: {'admin_dashboard': 200, 'teacher_dashboard': 403, 'dashboard': 403},
            self.teacher: {'admin_dashboard': 403, 'teacher_dashboard': 200, 'dashboard': 403},
            self.student: {'admin_dashboard': 403, 'teacher_dashboard': 403, 'dashboard': 200},
        }
        for user, pages in expected.items():
            for name, code in pages.items():
                self.assertEqual(self.status(user, name), code, f'{user.role} -> {name}')

    def test_student_pages_by_role(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('add_student'), STUDENT_FORM)
        slug = Student.objects.get().slug
        # admin: everything
        for name, args in [('student_list', ()), ('add_student', ()), ('view_student', (slug,)), ('edit_student', (slug,))]:
            self.assertEqual(self.status(self.admin, name, *args), 200, name)
        # teacher: can view, cannot change
        self.assertEqual(self.status(self.teacher, 'student_list'), 200)
        self.assertEqual(self.status(self.teacher, 'view_student', slug), 200)
        self.assertEqual(self.status(self.teacher, 'add_student'), 403)
        self.assertEqual(self.status(self.teacher, 'edit_student', slug), 403)
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.post(reverse('delete_student', args=[slug])).status_code, 403)
        self.assertTrue(Student.objects.exists())
        # student: no student management
        self.assertEqual(self.status(self.student, 'student_list'), 403)

    def test_sidebar_shows_only_allowed_links(self):
        self.client.force_login(self.teacher)
        page = self.client.get(reverse('student_list')).content.decode()
        self.assertIn('Student List', page)
        self.assertNotIn('Student Add', page)
        self.client.force_login(self.admin)
        page = self.client.get(reverse('student_list')).content.decode()
        self.assertIn('Student Add', page)

    def test_403_page_has_dashboard_link(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403)
        self.assertIn('Go to my dashboard', response.content.decode())


class DashboardStatsTests(TestCase):
    """Dashboards show real numbers from the database (Episode 2)."""

    def setUp(self):
        from django.core.management import call_command
        from io import StringIO
        call_command('seed_students', count=30, stdout=StringIO())
        make_user('teacher1@school.com', is_teacher=True)
        make_user('teacher2@school.com', is_teacher=True)

    def test_stats_match_database(self):
        from school.dashboard import get_dashboard_stats
        stats = get_dashboard_stats()
        self.assertEqual(stats['total_students'], 30)
        self.assertEqual(stats['total_teachers'], 2)
        self.assertEqual(sum(stats['chart_data']['class_counts']), 30)
        self.assertEqual(sum(stats['chart_data']['gender_counts']), 30)
        self.assertEqual(len(stats['recent_students']), 5)

    def test_classes_sorted_as_numbers(self):
        from school.dashboard import get_dashboard_stats
        labels = get_dashboard_stats()['chart_data']['class_labels']
        numbers = [int(label.split()[-1]) for label in labels]
        self.assertEqual(numbers, sorted(numbers))

    def test_admin_dashboard_shows_real_numbers(self):
        admin = CustomUser.objects.create_superuser(
            username='boss@school.com', email='boss@school.com', password='StrongPass123')
        self.client.force_login(admin)
        page = self.client.get(reverse('admin_dashboard')).content.decode()
        self.assertIn('<h3>30</h3>', page)
        self.assertIn('id="chart-data"', page)
        self.assertNotIn('50055', page)  # old fake number is gone

    def test_teacher_dashboard_has_no_add_button(self):
        teacher = CustomUser.objects.get(email='teacher1@school.com')
        self.client.force_login(teacher)
        page = self.client.get(reverse('teacher_dashboard')).content.decode()
        self.assertIn('Students by Class', page)
        self.assertNotIn('Add Student', page)
