from django import forms
from django.db.models import Sum

from academics.forms import StyledFormMixin
from .models import FeeStructure, Payment


class FeeStructureForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['school_class', 'title', 'amount', 'due_date']
        labels = {'school_class': 'Class'}
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'})}


class PaymentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['fee', 'amount', 'method']

    def __init__(self, *args, student, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student
        # Only the fees of this student's class
        self.fields['fee'].queryset = FeeStructure.objects.filter(
            school_class=student.section.school_class
        )

    def clean(self):
        cleaned = super().clean()
        fee, amount = cleaned.get('fee'), cleaned.get('amount')
        if fee and amount:
            paid = fee.payments.filter(student=self.student).aggregate(
                total=Sum('amount', default=0)
            )['total']
            balance = fee.amount - paid
            if amount > balance:
                self.add_error('amount', f'Only Rs. {balance} is left to pay for this fee.')
        return cleaned
