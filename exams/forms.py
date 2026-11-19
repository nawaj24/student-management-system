from django import forms

from academics.forms import StyledFormMixin
from .models import Exam


class ExamForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'school_class', 'start_date', 'full_marks', 'pass_marks']
        labels = {'school_class': 'Class'}
        widgets = {'start_date': forms.DateInput(attrs={'type': 'date'})}
