# Erweiterte Ausgaben-Modelle - zu expenses/models.py hinzufügen

from django.db import models
from users.models import CustomUser, Family
from budgets.models import Category
from django.utils import timezone
import datetime


class Expense(models.Model):
    EXPENSE_STATUS = [
        ('draft', 'Entwurf'),
        ('confirmed', 'Bestätigt'),
        ('pending', 'Ausstehend'),
    ]

    EXPENSE_TYPES = [
        ('single', 'Einzelausgabe'),
        ('recurring', 'Wiederkehrend'),
        ('split', 'Aufgeteilt'),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='expenses')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField()
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Neue Felder
    status = models.CharField(max_length=20, choices=EXPENSE_STATUS, default='confirmed')
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES, default='single')
    recurring_pattern = models.ForeignKey('RecurringPattern', null=True, blank=True, on_delete=models.SET_NULL)
    split_group = models.ForeignKey('ExpenseSplit', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.amount} CHF - {self.description}"

    def save(self, *args, **kwargs):
        # Erstelle wiederkehrende Ausgaben wenn nötig
        if self.expense_type == 'recurring' and self.recurring_pattern:
            self.create_recurring_expenses()
        super().save(*args, **kwargs)

    def create_recurring_expenses(self):
        """Erstellt zukünftige wiederkehrende Ausgaben"""
        if not self.recurring_pattern:
            return

        next_dates = self.recurring_pattern.get_next_dates(self.date)
        for next_date in next_dates:
            Expense.objects.get_or_create(
                family=self.family,
                user=self.user,
                category=self.category,
                date=next_date,
                defaults={
                    'amount': self.amount,
                    'description': self.description,
                    'status': 'pending',
                    'expense_type': 'recurring',
                    'recurring_pattern': self.recurring_pattern,
                }
            )


class RecurringPattern(models.Model):
    FREQUENCIES = [
        ('daily', 'Täglich'),
        ('weekly', 'Wöchentlich'),
        ('biweekly', 'Zweiwöchentlich'),
        ('monthly', 'Monatlich'),
        ('yearly', 'Jährlich'),
    ]

    frequency = models.CharField(max_length=20, choices=FREQUENCIES)
    interval = models.IntegerField(default=1)  # z.B. alle 2 Monate
    end_date = models.DateField(null=True, blank=True)
    max_occurrences = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_next_dates(self, start_date, count=12):
        """Generiert die nächsten Daten basierend auf dem Pattern"""
        dates = []
        current_date = start_date

        for i in range(count):
            if self.end_date and current_date > self.end_date:
                break
            if self.max_occurrences and i >= self.max_occurrences:
                break

            if self.frequency == 'daily':
                current_date += datetime.timedelta(days=self.interval)
            elif self.frequency == 'weekly':
                current_date += datetime.timedelta(weeks=self.interval)
            elif self.frequency == 'biweekly':
                current_date += datetime.timedelta(weeks=2 * self.interval)
            elif self.frequency == 'monthly':
                # Monatliche Berechnung
                if current_date.month == 12:
                    next_month = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    next_month = current_date.replace(month=current_date.month + self.interval)
                current_date = next_month
            elif self.frequency == 'yearly':
                current_date = current_date.replace(year=current_date.year + self.interval)

            dates.append(current_date)

        return dates


class ExpenseSplit(models.Model):
    """Gruppe für aufgeteilte Ausgaben"""
    description = models.CharField(max_length=255)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_split_details(self):
        """Gibt Details über die Aufteilung zurück"""
        splits = self.expense_split_items.all()
        return {
            'total': self.total_amount,
            'splits': [{
                'user': split.user,
                'amount': split.amount,
                'percentage': (split.amount / self.total_amount) * 100
            } for split in splits]
        }


class ExpenseSplitItem(models.Model):
    split_group = models.ForeignKey(ExpenseSplit, on_delete=models.CASCADE, related_name='expense_split_items')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='paid_splits')
    is_paid = models.BooleanField(default=False)


class ExpenseTemplate(models.Model):
    """Vorlagen für häufige Ausgaben"""
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    default_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description_template = models.CharField(max_length=255)
    use_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def create_expense(self, date=None, amount=None):
        """Erstellt Ausgabe basierend auf Template"""
        expense = Expense(
            family=self.family,
            user=self.user,
            category=self.category,
            amount=amount or self.default_amount,
            description=self.description_template,
            date=date or timezone.now().date(),
        )

        self.use_count += 1
        self.save()

        return expense


class ExpenseChangeLog(models.Model):
    """Protokolliert Änderungen an Ausgaben"""
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='change_logs')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=50)
    old_value = models.TextField()
    new_value = models.TextField()
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.expense} - {self.field_name} geändert von {self.user}"