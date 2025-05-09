# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Family


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    family_name = forms.CharField(max_length=100, help_text="Name deiner Familie oder deines Haushalts")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'family_name']

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['avatar']

        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'})
        }


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }


# users/forms.py (continued)
class FamilyMemberForm(UserCreationForm):
    email = forms.EmailField()

    ROLE_CHOICES = [
        ('ADULT', 'Erwachsener'),
        ('CHILD', 'Kind'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='CHILD'
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super(FamilyMemberForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name != 'role':
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})