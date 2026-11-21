from django.test import TestCase
from django.urls import reverse

from home_auth.models import CustomUser
from .models import Teacher

TEACHER_FORM = {
    'first_name': 'Ramesh', 'last_name': 'Yadav', 'teacher_id': 'T001', 'gender': 'Male',
    'date_of_birth': '1985-04-12', 'mobile_number': '9812345678', 'email': 'ramesh@school.com',
    'qualification': 'M.Sc', 'subject': 'Mathematics', 'joining_date': '2020-04-15',
    'address': 'Janakpur, Dhanusha',
}


def make_user(email, **roles):
    user = CustomUser.objects.create_user(username=email, email=email, password='StrongPass123')
    for role, value in roles.items():
        setattr(user, role, value)
    user.save()
    return user


class TeacherModuleTests(TestCase):
    """Teachers module (Episode 3)."""

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='admin@school.com', email='admin@school.com', password='StrongPass123')
        self.teacher_user = make_user('sita@school.com', is_teacher=True)
        self.student_user = make_user('aarav@school.com', is_student=True)
        self.client.force_login(self.admin)

    def test_admin_can_add_teacher(self):
        response = self.client.post(reverse('add_teacher'), TEACHER_FORM)
        self.assertRedirects(response, reverse('teacher_list'))
        teacher = Teacher.objects.get(teacher_id='T001')
        self.assertEqual(teacher.slug, 'ramesh-yadav-t001')

    def test_form_shows_errors_for_bad_data(self):
        Teacher.objects.create(**TEACHER_FORM)
        bad = dict(TEACHER_FORM, mobile_number='12345', email='not-an-email')
        page = self.client.post(reverse('add_teacher'), bad).content.decode()
        self.assertIn('Enter a 10-digit mobile number.', page)
        self.assertIn('Enter a valid email address.', page)
        self.assertIn('Teacher with this Teacher id already exists.', page)
        self.assertEqual(Teacher.objects.count(), 1)

    def test_edit_and_delete_teacher(self):
        teacher = Teacher.objects.create(**TEACHER_FORM)
        changed = dict(TEACHER_FORM, subject='Physics')
        self.client.post(reverse('edit_teacher', args=[teacher.slug]), changed)
        teacher.refresh_from_db()
        self.assertEqual(teacher.subject, 'Physics')
        self.client.post(reverse('delete_teacher', args=[teacher.slug]))
        self.assertFalse(Teacher.objects.exists())

    def test_search(self):
        Teacher.objects.create(**TEACHER_FORM)
        Teacher.objects.create(**dict(TEACHER_FORM, teacher_id='T002', first_name='Sunita',
                                      email='sunita@school.com', subject='English'))
        page = self.client.get(reverse('teacher_list'), {'q': 'english'}).content.decode()
        self.assertIn('Sunita', page)
        self.assertNotIn('Ramesh', page)

    def test_permissions(self):
        teacher = Teacher.objects.create(**TEACHER_FORM)
        self.client.force_login(self.teacher_user)
        self.assertEqual(self.client.get(reverse('teacher_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('teacher_detail', args=[teacher.slug])).status_code, 200)
        self.assertEqual(self.client.get(reverse('add_teacher')).status_code, 403)
        self.assertEqual(self.client.post(reverse('delete_teacher', args=[teacher.slug])).status_code, 403)
        self.client.force_login(self.student_user)
        self.assertEqual(self.client.get(reverse('teacher_list')).status_code, 403)

    def test_dashboard_counts_teacher_records(self):
        Teacher.objects.create(**TEACHER_FORM)
        page = self.client.get(reverse('admin_dashboard')).content.decode()
        self.assertIn('<h3>1</h3>', page)
