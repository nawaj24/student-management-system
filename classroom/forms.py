from django import forms

from academics.forms import StyledFormMixin
from .models import SchoolClass, Section


class SchoolClassForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'order']


class SectionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Section
        fields = ['school_class', 'name', 'class_teacher', 'room']
        labels = {'school_class': 'Class'}

    def clean_name(self):
        return self.cleaned_data['name'].strip().upper()
