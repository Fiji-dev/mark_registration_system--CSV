from django import forms
from django.core.exceptions import ValidationError

# Form for Inputting Marks
class InputMarkForm(forms.Form):
    student_id = forms.CharField(max_length=50, label='Student ID')
    student_name = forms.CharField(max_length=100, label='Student Name')
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')], label='Gender')
    module_code = forms.CharField(max_length=50, label='Module Code')
    module_name = forms.CharField(max_length=100, label='Module Name')
    coursework1 = forms.IntegerField(min_value=0, max_value=100, label='Coursework 1')
    coursework2 = forms.IntegerField(min_value=0, max_value=100, label='Coursework 2')
    coursework3 = forms.IntegerField(min_value=0, max_value=100, label='Coursework 3')
    date_of_entry = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Date of Entry')

    # Custom validation to check that no individual coursework mark exceeds 100
    def clean_coursework1(self):
        coursework1 = self.cleaned_data.get('coursework1')
        if coursework1 > 100:
            raise ValidationError("Coursework 1 cannot exceed 100.")
        return coursework1

    def clean_coursework2(self):
        coursework2 = self.cleaned_data.get('coursework2')
        if coursework2 > 100:
            raise ValidationError("Coursework 2 cannot exceed 100.")
        return coursework2

    def clean_coursework3(self):
        coursework3 = self.cleaned_data.get('coursework3')
        if coursework3 > 100:
            raise ValidationError("Coursework 3 cannot exceed 100.")
        return coursework3

# Form for Updating Marks
class UpdateMarkForm(forms.Form):
    student_id = forms.CharField(max_length=50, label='Student ID')
    module_code = forms.CharField(max_length=50, label='Module Code')
    coursework1 = forms.IntegerField(min_value=0, max_value=100, label='Coursework 1')
    coursework2 = forms.IntegerField(min_value=0, max_value=100, label='Coursework 2')
    coursework3 = forms.IntegerField(min_value=0, max_value=100, label='Coursework 3')
    date_of_entry = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Date of Entry')

    # Custom validation to check that no individual coursework mark exceeds 100
    def clean_coursework1(self):
        coursework1 = self.cleaned_data.get('coursework1')
        if coursework1 > 100:
            raise ValidationError("Coursework 1 cannot exceed 100.")
        return coursework1

    def clean_coursework2(self):
        coursework2 = self.cleaned_data.get('coursework2')
        if coursework2 > 100:
            raise ValidationError("Coursework 2 cannot exceed 100.")
        return coursework2

    def clean_coursework3(self):
        coursework3 = self.cleaned_data.get('coursework3')
        if coursework3 > 100:
            raise ValidationError("Coursework 3 cannot exceed 100.")
        return coursework3

    def clean(self):
        cleaned_data = super().clean()
        coursework1 = cleaned_data.get("coursework1")
        coursework2 = cleaned_data.get("coursework2")
        coursework3 = cleaned_data.get("coursework3")

        # Check total marks (no limit on total marks)
        if coursework1 is not None and coursework2 is not None and coursework3 is not None:
            total_marks = coursework1 + coursework2 + coursework3
            # You can choose to validate total marks here if needed (e.g., max 300 total marks)
            # For example, you can enforce the total marks to be between 0 and 300.
            # if total_marks > 300:
            #     raise ValidationError("Total marks cannot exceed 300.")

        return cleaned_data
