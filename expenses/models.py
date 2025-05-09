from django.db import models
from users.models import CustomUser, Family
from budgets.models import Category


class Expense(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='expenses')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField()
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} CHF - {self.description}"