# Erweiterte Benutzer-Modelle - zu users/models.py hinzufügen

from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from expenses.models import Expense


class Family(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    # Neue Einstellungen
    require_approval_amount = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    child_spending_limit_daily = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    child_spending_limit_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    enable_child_notifications = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('ADULT', 'Erwachsener'),
        ('CHILD', 'Kind'),
        ('ADMIN', 'Administrator'),
    ]

    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, related_name='members')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='ADULT')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Persönliche Einstellungen
    personal_budget_enabled = models.BooleanField(default=False)
    personal_budget_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notification_preferences = models.JSONField(default=dict)

    def __str__(self):
        return self.username

    def can_approve_expenses(self):
        """Prüft ob Benutzer Ausgaben genehmigen kann"""
        return self.role in ['ADULT', 'ADMIN']

    def check_spending_limit(self, amount):
        """Prüft ob Ausgabe Limit überschreitet"""
        if self.role != 'CHILD':
            return True

        # Tägliches Limit prüfen
        today_expenses = Expense.objects.filter(
            user=self,
            date=timezone.now().date()
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        if today_expenses + amount > self.family.child_spending_limit_daily:
            return False

        # Monatliches Limit prüfen
        current_month = timezone.now().date().replace(day=1)
        month_expenses = Expense.objects.filter(
            user=self,
            date__gte=current_month
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        if month_expenses + amount > self.family.child_spending_limit_monthly:
            return False

        return True


class PersonalBudget(models.Model):
    """Persönliche Budgets innerhalb des Familienbudgets"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='personal_budgets')
    family_budget = models.ForeignKey('budgets.Budget', on_delete=models.CASCADE)
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)

    def available_amount(self):
        """Verfügbarer Betrag im persönlichen Budget"""
        spent = Expense.objects.filter(
            user=self.user,
            date__year=self.family_budget.month.year,
            date__month=self.family_budget.month.month
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        return self.allocated_amount - spent


class ExpenseApproval(models.Model):
    """Genehmigungen für Ausgaben"""
    APPROVAL_STATUS = [
        ('pending', 'Ausstehend'),
        ('approved', 'Genehmigt'),
        ('rejected', 'Abgelehnt'),
    ]

    expense = models.ForeignKey('expenses.Expense', on_delete=models.CASCADE, related_name='approvals')
    requested_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='expense_requests')
    approver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='expense_approvals', null=True,
                                 blank=True)
    status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    decision_date = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)

    def approve(self, approver, comment=''):
        """Genehmigt die Ausgabe"""
        self.approver = approver
        self.status = 'approved'
        self.decision_date = timezone.now()
        self.comment = comment
        self.save()

        # Ausgabe als bestätigt markieren
        self.expense.status = 'confirmed'
        self.expense.save()

    def reject(self, approver, comment=''):
        """Lehnt die Ausgabe ab"""
        self.approver = approver
        self.status = 'rejected'
        self.decision_date = timezone.now()
        self.comment = comment
        self.save()


class Account(models.Model):
    """Verschiedene Konten innerhalb einer Familie"""
    ACCOUNT_TYPES = [
        ('joint', 'Gemeinsames Konto'),
        ('personal', 'Persönliches Konto'),
        ('savings', 'Sparkonto'),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    owners = models.ManyToManyField(CustomUser, related_name='accounts')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"


class Notification(models.Model):
    """Benachrichtigungssystem"""
    NOTIFICATION_TYPES = [
        ('expense_approval', 'Ausgabengenehmigung'),
        ('budget_warning', 'Budget-Warnung'),
        ('saving_reminder', 'Spar-Erinnerung'),
        ('expense_limit', 'Ausgabenlimit'),
        ('milestone_reached', 'Meilenstein erreicht'),
    ]

    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications', null=True,
                               blank=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    action_url = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def mark_as_read(self):
        self.is_read = True
        self.save()


class NotificationPreference(models.Model):
    """Benachrichtigungseinstellungen"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='notification_settings')

    # Email-Benachrichtigungen
    email_expense_approval = models.BooleanField(default=True)
    email_budget_warning = models.BooleanField(default=True)
    email_saving_reminder = models.BooleanField(default=True)
    email_weekly_summary = models.BooleanField(default=True)

    # In-App Benachrichtigungen
    app_expense_approval = models.BooleanField(default=True)
    app_budget_warning = models.BooleanField(default=True)
    app_saving_reminder = models.BooleanField(default=True)

    # Zeiteinstellungen
    daily_summary_time = models.TimeField(default='18:00')
    weekly_summary_day = models.IntegerField(default=6)  # 0=Montag, 6=Sonntag