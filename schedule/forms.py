from django import forms

from academics.forms import StyledFormMixin
from .models import Event, Period


class PeriodForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Period
        fields = ['section', 'day', 'number', 'subject', 'teacher', 'start_time', 'end_time']
        labels = {'number': 'Period number'}
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class EventForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'kind', 'start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
