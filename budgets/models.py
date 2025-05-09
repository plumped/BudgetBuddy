from django.db import models
from users.models import Family


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='money')

    def __str__(self):
        return self.name


class Budget(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='budgets')
    month = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.family.name} - {self.month.strftime('%B %Y')}"

    class Meta:
        unique_together = ['family', 'month']


class BudgetCategory(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.category.name}: {self.amount} CHF"