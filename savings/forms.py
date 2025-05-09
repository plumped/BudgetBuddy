from django import forms
from django.utils.timezone import localdate
from .models import SavingGoal, SavingTransaction


class SavingGoalForm(forms.ModelForm):
    target_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = SavingGoal
        fields = ['title', 'description', 'target_amount', 'target_date', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class SavingTransactionForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'},
            format='%Y-%m-%d'  # wichtig
        ),
        initial=localdate,
        input_formats=['%Y-%m-%d']  # Format auch beim Einlesen akzeptieren
    )

    class Meta:
        model = SavingTransaction
        fields = ['amount', 'transaction_type', 'date', 'note']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }
