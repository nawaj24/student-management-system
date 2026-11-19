from django import forms

from .models import Department, Subject


class StyledFormMixin:
    """Bootstrap styling + upper-case codes for both forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'form-control'

    def clean_code(self):
        return self.cleaned_data['code'].strip().upper()


class DepartmentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'head', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class SubjectForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'department', 'teachers']
        widgets = {'teachers': forms.CheckboxSelectMultiple}
