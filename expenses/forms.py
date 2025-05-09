from django import forms
from django.utils.timezone import localdate
from .models import Expense

class ExpenseForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
            },
            format='%Y-%m-%d'  # ganz wichtig
        ),
        initial=localdate,
        input_formats=['%Y-%m-%d']  # sicherstellen, dass das Format angenommen wird
    )

    class Meta:
        model = Expense
        fields = ['category', 'amount', 'description', 'date', 'receipt_image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
