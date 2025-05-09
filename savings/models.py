from django.db import models
from users.models import Family, CustomUser


class SavingGoal(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='saving_goals')
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_goals')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='goals/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return int((self.current_amount / self.target_amount) * 100)


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

    def __str__(self):
        return f"{self.get_transaction_type_display()}: {self.amount} CHF"