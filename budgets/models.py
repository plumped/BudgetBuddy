from django.db import models
from users.models import Family
from decimal import Decimal


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

    @property
    def total_amount(self):
        return sum(category.amount for category in self.categories.all())

    @property
    def total_spent(self):
        from expenses.models import Expense  # lazy import to avoid circular import
        return sum(
            expense.amount for expense in Expense.objects.filter(
                family=self.family,
                category__in=self.categories.values_list('category', flat=True),
                date__year=self.month.year,
                date__month=self.month.month
            )
        )

    @property
    def remaining_amount(self):
        return self.total_amount - self.total_spent

    @property
    def status(self):
        remaining = self.remaining_amount
        total = self.total_amount
        if remaining >= total * Decimal("0.25"):
            return 'on_track'
        elif remaining >= 0:
            return 'warning'
        return 'over_budget'


class BudgetCategory(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.category.name}: {self.amount} CHF"
