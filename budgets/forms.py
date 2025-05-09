from django import forms
from django.utils import timezone
from .models import Budget, BudgetCategory, Category


class BudgetForm(forms.ModelForm):
    month = forms.DateField(
        input_formats=['%Y-%m'],
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}),
        initial=timezone.now().date().replace(day=1)
    )

    class Meta:
        model = Budget
        fields = ['month']


class BudgetCategoryForm(forms.ModelForm):
    class Meta:
        model = BudgetCategory
        fields = ['category', 'amount']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


BudgetCategoryFormSet = forms.inlineformset_factory(
    Budget, BudgetCategory, form=BudgetCategoryForm,
    extra=3, can_delete=True
)