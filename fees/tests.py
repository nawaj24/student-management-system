import datetime
from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from home_auth.models import CustomUser
from school.tests import make_user
from student.models import Student
from .models import FeeStructure, Payment


class FeeTests(TestCase):
    """Fees (Episode 8)."""

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='admin@school.com', email='admin@school.com', password='StrongPass123')
        self.client.force_login(self.admin)
        call_command('seed_classes', stdout=StringIO())
        call_command('seed_students', count=10, stdout=StringIO())
        self.student = Student.objects.first()
        self.fee = FeeStructure.objects.create(
            school_class=self.student.section.school_class, title='Tuition · Mangsir',
            amount=Decimal('2000'), due_date=timezone.localdate() - datetime.timedelta(days=1))
        self.url = reverse('student_fees', args=[self.student.slug])

    def pay(self, amount):
        return self.client.post(self.url, {'fee': self.fee.pk, 'amount': amount, 'method': 'esewa'})

    def test_partial_then_full_payment(self):
        response = self.pay('500')
        payment = Payment.objects.get()
        self.assertRedirects(response, reverse('fee_receipt', args=[payment.pk]))
        self.assertEqual(payment.received_by, self.admin)
        line = self.client.get(self.url).context['lines'][0]
        self.assertEqual((line['balance'], line['status']), (Decimal('1500'), 'Partial'))
        self.pay('1500')
        line = self.client.get(self.url).context['lines'][0]
        self.assertEqual((line['balance'], line['status']), (Decimal('0'), 'Paid'))

    def test_cannot_pay_more_than_balance(self):
        self.pay('1500')
        response = self.pay('600')
        self.assertContains(response, 'Only Rs. 500.00 is left')
        self.assertEqual(Payment.objects.count(), 1)

    def test_overdue_status_and_receipt(self):
        self.assertEqual(self.client.get(self.url).context['lines'][0]['status'], 'Overdue')
        self.pay('2000')
        receipt = self.client.get(reverse('fee_receipt', args=[Payment.objects.get().pk]))
        self.assertContains(receipt, 'RCP-00001')

    def test_pending_dues(self):
        self.pay('500')
        rows = self.client.get(reverse('pending_dues')).context['rows']
        row = next(r for r in rows if r['student'] == self.student)
        self.assertEqual(row['due'], Decimal('1500'))

    def test_only_admin(self):
        self.client.force_login(make_user('sita@school.com', is_teacher=True))
        self.assertEqual(self.client.get(reverse('fee_list')).status_code, 403)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_seed_fees(self):
        call_command('seed_fees', stdout=StringIO())
        payments = Payment.objects.count()
        call_command('seed_fees', stdout=StringIO())
        self.assertEqual(FeeStructure.objects.count(), 30)  # 3 per class (setUp's Mangsir fee is reused)
        self.assertEqual(Payment.objects.count(), payments)
