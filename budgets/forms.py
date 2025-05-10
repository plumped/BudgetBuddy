# Erweiterte Budget-Forms - zu budgets/forms.py hinzufügen

from django import forms
from django.utils import timezone
from .models import Budget, BudgetCategory, Category, BudgetTemplate


class BudgetForm(forms.ModelForm):
    month = forms.DateField(
        input_formats=['%Y-%m'],
        widget=forms.DateInput(attrs={'type': 'month', 'class': 'form-control'}),
        initial=timezone.now().date().replace(day=1)
    )

    carry_over = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Überschuss vom vorherigen Monat übertragen"
    )

    class Meta:
        model = Budget
        fields = ['month', 'budget_type', 'frequency', 'end_date']
        widgets = {
            'budget_type': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # end_date nur bei custom budget anzeigen
        self.fields['end_date'].widget = forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control', 'style': 'display:none;'}
        )


class BudgetCategoryForm(forms.ModelForm):
    class Meta:
        model = BudgetCategory
        fields = ['category', 'amount', 'is_flexible']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'is_flexible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


BudgetCategoryFormSet = forms.inlineformset_factory(
    Budget, BudgetCategory, form=BudgetCategoryForm,
    extra=3, can_delete=True
)


class BudgetTemplateForm(forms.ModelForm):
    class Meta:
        model = BudgetTemplate
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BulkCategoryForm(forms.Form):
    """Form für Bulk-Aktionen auf Ausgaben"""
    action = forms.ChoiceField(choices=[
        ('categorize', 'Kategorisieren'),
        ('approve', 'Genehmigen'),
        ('delete', 'Löschen'),
    ])

    new_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    selected_expenses = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        new_category = cleaned_data.get('new_category')

        if action == 'categorize' and not new_category:
            raise forms.ValidationError('Bitte wähle eine Kategorie aus.')

        return cleaned_data