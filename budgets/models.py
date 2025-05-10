# Erweiterte Budget-Modelle - zu budgets/models.py hinzufügen

from django.db import models
from users.models import Family
from decimal import Decimal
import datetime


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='money')

    def __str__(self):
        return self.name


class Budget(models.Model):
    BUDGET_TYPES = [
        ('monthly', 'Monatlich'),
        ('weekly', 'Wöchentlich'),
        ('custom', 'Benutzerdefiniert'),
    ]

    BUDGET_FREQUENCIES = [
        ('once', 'Einmalig'),
        ('recurring', 'Wiederkehrend'),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='budgets')
    month = models.DateField()  # Kann auch Startdatum sein
    end_date = models.DateField(null=True, blank=True)  # Für flexible Zeiträume
    budget_type = models.CharField(max_length=20, choices=BUDGET_TYPES, default='monthly')
    frequency = models.CharField(max_length=20, choices=BUDGET_FREQUENCIES, default='once')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    copied_from = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    # Für Budget-Übertragung
    carryover_from_previous = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    carryover_to_next = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.family.name} - {self.month.strftime('%B %Y')}"

    class Meta:
        unique_together = ['family', 'month']

    @property
    def total_amount(self):
        return sum(category.amount for category in self.categories.all()) + self.carryover_from_previous

    @property
    def total_spent(self):
        from expenses.models import Expense
        if self.budget_type == 'monthly':
            return sum(
                expense.amount for expense in Expense.objects.filter(
                    family=self.family,
                    category__in=self.categories.values_list('category', flat=True),
                    date__year=self.month.year,
                    date__month=self.month.month
                )
            )
        else:
            return sum(
                expense.amount for expense in Expense.objects.filter(
                    family=self.family,
                    category__in=self.categories.values_list('category', flat=True),
                    date__gte=self.month,
                    date__lte=self.end_date or datetime.date.today()
                )
            )

    @property
    def remaining_amount(self):
        remaining = self.total_amount - self.total_spent
        self.carryover_to_next = remaining if remaining > 0 else 0
        return remaining

    @property
    def status(self):
        remaining = self.remaining_amount
        total = self.total_amount
        if remaining >= total * Decimal("0.25"):
            return 'on_track'
        elif remaining >= 0:
            return 'warning'
        return 'over_budget'

    def copy_to_next_period(self):
        """Kopiert Budget zum nächsten Zeitraum"""
        if self.budget_type == 'monthly':
            next_month = self.month + datetime.timedelta(days=32)
            next_month = next_month.replace(day=1)
        else:
            duration = (self.end_date - self.month).days
            next_month = self.end_date + datetime.timedelta(days=1)

        new_budget = Budget.objects.create(
            family=self.family,
            month=next_month,
            end_date=next_month + datetime.timedelta(days=duration) if self.budget_type != 'monthly' else None,
            budget_type=self.budget_type,
            frequency=self.frequency,
            copied_from=self,
            carryover_from_previous=self.carryover_to_next
        )

        # Kategorien kopieren
        for budget_category in self.categories.all():
            BudgetCategory.objects.create(
                budget=new_budget,
                category=budget_category.category,
                amount=budget_category.amount
            )

        return new_budget


class BudgetCategory(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_flexible = models.BooleanField(default=False)  # Kann Budget von anderen Kategorien "leihen"

    def __str__(self):
        return f"{self.category.name}: {self.amount} CHF"


class BudgetTemplate(models.Model):
    """Vorlagen für schnelles Budget-Erstellen"""
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def apply_to_budget(self, budget):
        """Wendet Template auf Budget an"""
        for template_category in self.template_categories.all():
            BudgetCategory.objects.create(
                budget=budget,
                category=template_category.category,
                amount=template_category.default_amount
            )


class BudgetTemplateCategory(models.Model):
    template = models.ForeignKey(BudgetTemplate, on_delete=models.CASCADE, related_name='template_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    default_amount = models.DecimalField(max_digits=10, decimal_places=2)