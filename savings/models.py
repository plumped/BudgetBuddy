# Erweiterte Sparziel-Modelle - zu savings/models.py hinzufügen

from django.db import models
from users.models import Family, CustomUser
from budgets.models import Budget
from decimal import Decimal


class SavingCategory(models.Model):
    """Kategorien für Sparziele"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='piggy-bank')
    color = models.CharField(max_length=7, default='#0d6efd')  # Hex color

    def __str__(self):
        return self.name


class SavingGoal(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'Hoch'),
        ('medium', 'Mittel'),
        ('low', 'Niedrig'),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='saving_goals')
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_goals')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(SavingCategory, null=True, blank=True, on_delete=models.SET_NULL)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    image = models.ImageField(upload_to='goals/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Automatisches Sparen
    auto_save_enabled = models.BooleanField(default=False)
    auto_save_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    auto_save_fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    linked_budget = models.ForeignKey(Budget, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return min(int((self.current_amount / self.target_amount) * 100), 100)

    @property
    def days_remaining(self):
        if self.target_date:
            return (self.target_date - timezone.now().date()).days
        return None

    @property
    def monthly_savings_required(self):
        if not self.target_date:
            return None

        days_remaining = self.days_remaining
        if days_remaining <= 0:
            return None

        months_remaining = days_remaining / 30
        remaining_amount = self.target_amount - self.current_amount

        return remaining_amount / months_remaining if months_remaining > 0 else 0

    def auto_save_from_budget(self):
        """Führt automatisches Sparen vom Budget aus"""
        if not self.auto_save_enabled or not self.linked_budget:
            return

        budget_remaining = self.linked_budget.remaining_amount

        if self.auto_save_percentage:
            amount = budget_remaining * (self.auto_save_percentage / 100)
        elif self.auto_save_fixed_amount:
            amount = min(self.auto_save_fixed_amount, budget_remaining)
        else:
            return

        if amount > 0:
            SavingTransaction.objects.create(
                goal=self,
                user=self.creator,
                amount=amount,
                transaction_type='DEPOSIT',
                date=timezone.now().date(),
                note=f"Automatisches Sparen ({self.auto_save_percentage}% vom Budget)" if self.auto_save_percentage else "Automatisches Sparen (fester Betrag)"
            )

            self.current_amount += amount
            self.save()


class SavingMilestone(models.Model):
    """Meilensteine für Sparziele"""
    goal = models.ForeignKey(SavingGoal, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=100)
    target_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reward_description = models.TextField(blank=True)
    achieved = models.BooleanField(default=False)
    achieved_at = models.DateTimeField(null=True, blank=True)

    def check_achievement(self):
        """Prüft ob Meilenstein erreicht wurde"""
        if not self.achieved and self.goal.current_amount >= self.target_amount:
            self.achieved = True
            self.achieved_at = timezone.now()
            self.save()

            # Benachrichtigung oder Belohnung auslösen
            self.trigger_reward()

    def trigger_reward(self):
        """Trigger für Belohnung bei Erreichen des Meilensteins"""
        # Hier könnte eine Benachrichtigung oder andere Aktion ausgelöst werden
        pass


class SavingTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('DEPOSIT', 'Einzahlung'),
        ('WITHDRAWAL', 'Auszahlung'),
    ]

    goal = models.ForeignKey(SavingGoal, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saving_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_automatic = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_transaction_type_display()}: {self.amount} CHF"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Sparziel-Betrag aktualisieren
        if self.transaction_type == 'DEPOSIT':
            self.goal.current_amount = models.F('current_amount') + self.amount
        elif self.transaction_type == 'WITHDRAWAL':
            self.goal.current_amount = models.F('current_amount') - self.amount

        self.goal.save()
        self.goal.refresh_from_db()

        # Meilensteine prüfen
        for milestone in self.goal.milestones.all():
            milestone.check_achievement()


class SavingChallenge(models.Model):
    """Spar-Challenges für Familien"""
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    participants = models.ManyToManyField(CustomUser, through='ChallengeParticipant')

    def add_participant(self, user, personal_target=None):
        """Fügt Teilnehmer zur Challenge hinzu"""
        ChallengeParticipant.objects.get_or_create(
            challenge=self,
            user=user,
            defaults={'personal_target': personal_target or 0}
        )


class ChallengeParticipant(models.Model):
    challenge = models.ForeignKey(SavingChallenge, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    personal_target = models.DecimalField(max_digits=10, decimal_places=2)
    amount_saved = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    joined_at = models.DateTimeField(auto_now_add=True)