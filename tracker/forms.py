from django import forms
from .models import JobApplication


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["company_name", "position", "status", "applied_date", "link", "notes"]
        widgets = {
            "company_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Company Name"}),
            "position": forms.TextInput(attrs={"class": "form-control", "placeholder": "Position"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "applied_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "link": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Notes"}),
        }


class JobApplicationEditForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["company_name", "position", "status", "applied_date", "link", "notes"]
        widgets = {
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "position": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "applied_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "link": forms.URLInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select form-select-sm"}),
        }


class NotesEditForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm Password"}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        from django.contrib.auth.models import User

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get("password1")
        pw2 = cleaned.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned
