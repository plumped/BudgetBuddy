# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfilePictureForm, FamilyForm, FamilyMemberForm
from .models import Family, CustomUser


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Familienname aus Formular extrahieren
            family_name = form.cleaned_data.get('family_name')

            # Benutzer erstellen, aber noch nicht speichern
            user = form.save(commit=False)

            # Neue Familie erstellen
            family = Family.objects.create(name=family_name)

            # Benutzer mit Familie verknüpfen und speichern
            user.family = family
            user.role = 'ADULT'  # Standardmäßig als Erwachsener
            user.save()

            messages.success(request, f'Dein Konto wurde erfolgreich erstellt! Du kannst dich jetzt anmelden.')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_pic_form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)

        if user_form.is_valid() and profile_pic_form.is_valid():
            user_form.save()
            profile_pic_form.save()
            messages.success(request, 'Dein Profil wurde aktualisiert!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_pic_form = ProfilePictureForm(instance=request.user)

    context = {
        'user_form': user_form,
        'profile_pic_form': profile_pic_form
    }

    return render(request, 'users/profile.html', context)


@login_required
def family_view(request):
    family = request.user.family

    if not family:
        messages.error(request, "Du bist aktuell keiner Familie zugeordnet.")
        return redirect('dashboard')  # oder wohin du willst

    family_members = CustomUser.objects.filter(family=family)

    if request.method == 'POST':
        family_form = FamilyForm(request.POST, instance=family)
        if family_form.is_valid():
            family_form.save()
            messages.success(request, 'Die Familieneinstellungen wurden aktualisiert!')
            return redirect('family')
    else:
        family_form = FamilyForm(instance=family)

    context = {
        'family': family,
        'family_members': family_members,
        'family_form': family_form
    }

    return render(request, 'users/family.html', context)



@login_required
def add_family_member(request):
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST)
        if form.is_valid():
            # Familienmitglied erstellen, aber noch nicht speichern
            member = form.save(commit=False)

            # Mit bestehender Familie des aktuellen Benutzers verknüpfen
            member.family = request.user.family
            member.role = form.cleaned_data.get('role')  # <-- hinzufügen!
            # Passwort setzen und Benutzer speichern
            member.set_password(form.cleaned_data.get('password1'))
            member.save()

            messages.success(request, f'Das Familienmitglied {member.username} wurde erfolgreich hinzugefügt!')
            return redirect('family')
    else:
        form = FamilyMemberForm()

    return render(request, 'users/add_family_member.html', {'form': form})

@login_required
def remove_family_member(request, member_id):
    member = CustomUser.objects.filter(id=member_id, family=request.user.family).first()
    if not member:
        messages.error(request, "Mitglied nicht gefunden oder gehört nicht zu deiner Familie.")
    elif member == request.user:
        messages.error(request, "Du kannst dich nicht selbst entfernen.")
    else:
        member.family = None
        member.save()
        messages.success(request, f"{member.username} wurde aus der Familie entfernt.")
    return redirect('family')

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