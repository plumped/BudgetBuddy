from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
import datetime

from expenses.models import Expense
from budgets.models import Budget, BudgetCategory
from savings.models import SavingGoal


@login_required
def dashboard(request):
    # Aktuelle Familie des Benutzers
    family = request.user.family

    # Aktuelles Datum für Berechnungen
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    next_month = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)

    # Aktives Budget für den aktuellen Monat
    try:
        current_budget = Budget.objects.get(family=family, month__year=today.year, month__month=today.month)
        budget_categories = current_budget.categories.all()
    except Budget.DoesNotExist:
        current_budget = None
        budget_categories = []

    # Ausgaben des aktuellen Monats
    current_expenses = Expense.objects.filter(
        family=family,
        date__gte=current_month_start,
        date__lt=next_month
    )

    # Gesamtausgaben nach Kategorie gruppieren
    expenses_by_category = {}
    for expense in current_expenses:
        category_name = expense.category.name if expense.category else "Sonstige"
        if category_name not in expenses_by_category:
            expenses_by_category[category_name] = 0
        expenses_by_category[category_name] += expense.amount

    # Budgetübersicht erstellen
    budget_overview = []
    for budget_cat in budget_categories:
        cat_name = budget_cat.category.name
        spent = expenses_by_category.get(cat_name, 0)
        budget_amount = budget_cat.amount

        # Berechne verbleibenden Betrag und Prozentsatz
        remaining = budget_amount - spent
        if budget_amount > 0:
            percentage = (spent / budget_amount) * 100
        else:
            percentage = 0

        budget_overview.append({
            'category': cat_name,
            'icon': budget_cat.category.icon,
            'budget': budget_amount,
            'spent': spent,
            'remaining': remaining,
            'percentage': min(percentage, 100),  # Maximal 100%
        })

    # Aktive Sparziele
    saving_goals = SavingGoal.objects.filter(family=family)

    # Letzte Transaktionen
    recent_expenses = Expense.objects.filter(
        family=family
    ).order_by('-date')[:5]

    # Gesamtausgaben im aktuellen Monat
    total_expenses = current_expenses.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'budget_overview': budget_overview,
        'saving_goals': saving_goals,
        'recent_expenses': recent_expenses,
        'total_expenses': total_expenses,
        'current_month': today.strftime('%B %Y'),
    }

    return render(request, 'dashboard/dashboard.html', context)