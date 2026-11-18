from django import forms

from .models import Teacher


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        exclude = ['slug']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Give every field the Bootstrap look used by the template
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_mobile_number(self):
        mobile = self.cleaned_data['mobile_number']
        if not mobile.isdigit() or len(mobile) != 10:
            raise forms.ValidationError('Enter a 10-digit mobile number.')
        return mobile
