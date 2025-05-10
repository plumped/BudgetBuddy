# Erweiterte Budget-Views - zu budgets/views.py hinzufügen

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import datetime
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Budget, BudgetCategory, Category, BudgetTemplate, BudgetTemplateCategory
from .forms import BudgetForm, BudgetCategoryFormSet, BudgetTemplateForm
from expenses.models import Expense


@login_required
def budget_list(request):
    family = request.user.family
    budgets = Budget.objects.filter(family=family).order_by('-month')

    # Aktuelles Budget ermitteln
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    next_month = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)

    try:
        current_budget = Budget.objects.get(
            family=family,
            month__gte=current_month_start,
            month__lt=next_month
        )
    except Budget.DoesNotExist:
        current_budget = None

    # Anzahl Kategorien
    categories_count = Category.objects.count()

    # Budget-Templates
    templates = BudgetTemplate.objects.filter(family=family)

    context = {
        'budgets': budgets,
        'current_budget': current_budget,
        'categories_count': categories_count,
        'templates': templates,
    }

    return render(request, 'budgets/budget_list.html', context)


@login_required
def create_budget(request):
    family = request.user.family

    # Budget-Templates laden
    templates = BudgetTemplate.objects.filter(family=family)

    # Budget aus Template erstellen
    template_id = request.GET.get('template')
    template = None
    if template_id:
        template = get_object_or_404(BudgetTemplate, id=template_id, family=family)

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        formset = BudgetCategoryFormSet(request.POST)

        if form.is_valid():
            budget = form.save(commit=False)
            budget.family = family

            # Carryover vom vorherigen Budget
            if 'carry_over' in request.POST:
                previous_budget = Budget.objects.filter(
                    family=family,
                    month__lt=budget.month
                ).order_by('-month').first()

                if previous_budget:
                    budget.carryover_from_previous = previous_budget.carryover_to_next

            budget.save()

            formset = BudgetCategoryFormSet(request.POST, instance=budget)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Budget erfolgreich erstellt!')

                # Wenn rekurrierend, nächstes Budget erstellen
                if budget.frequency == 'recurring':
                    budget.copy_to_next_period()

                return redirect('budget_list')
    else:
        form = BudgetForm()
        if template:
            # Budget mit Template vorausfüllen
            budget = Budget(family=family, month=timezone.now().date().replace(day=1))
            template.apply_to_budget(budget)
            formset = BudgetCategoryFormSet(instance=budget)
        else:
            formset = BudgetCategoryFormSet()

    context = {
        'form': form,
        'formset': formset,
        'templates': templates,
        'template': template,
        'categories': Category.objects.all(),
    }

    return render(request, 'budgets/create_budget.html', context)


@login_required
def create_budget_template(request):
    family = request.user.family

    if request.method == 'POST':
        form = BudgetTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.family = family
            template.save()

            # Kategorien hinzufügen
            for key, value in request.POST.items():
                if key.startswith('category_') and key.endswith('_amount'):
                    category_id = key.split('_')[1]
                    amount = value

                    if amount:
                        category = get_object_or_404(Category, id=category_id)
                        BudgetTemplateCategory.objects.create(
                            template=template,
                            category=category,
                            default_amount=amount
                        )

            messages.success(request, 'Budget-Vorlage erstellt!')
            return redirect('budget_list')
    else:
        form = BudgetTemplateForm()

    context = {
        'form': form,
        'categories': Category.objects.all(),
    }

    return render(request, 'budgets/create_template.html', context)


@login_required
@require_POST
def copy_budget(request, budget_id):
    """Kopiert Budget zum nächsten Zeitraum"""
    budget = get_object_or_404(Budget, id=budget_id, family=request.user.family)
    new_budget = budget.copy_to_next_period()

    messages.success(request, f'Budget kopiert für {new_budget.month.strftime("%B %Y")}')
    return redirect('budget_detail', budget_id=new_budget.id)


@login_required
def budget_analysis(request):
    """Erweiterte Budget-Analyse"""
    family = request.user.family
    period = request.GET.get('period', 'year')

    # Zeitraum bestimmen
    today = timezone.now().date()
    if period == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    elif period == '6months':
        start_date = today - datetime.timedelta(days=180)
        end_date = today
    else:
        start_date = today.replace(day=1) - datetime.timedelta(days=90)
        end_date = today

    # Budget-Performance über Zeit
    budgets = Budget.objects.filter(
        family=family,
        month__gte=start_date,
        month__lte=end_date
    ).order_by('month')

    # Analyse-Daten
    budget_data = []
    for budget in budgets:
        budget_data.append({
            'month': budget.month.strftime('%Y-%m'),
            'planned': float(budget.total_amount),
            'spent': float(budget.total_spent),
            'saved': float(budget.remaining_amount),
            'status': budget.status,
        })

    # Kategorien-Performance
    category_performance = []
    for category in Category.objects.all():
        planned = BudgetCategory.objects.filter(
            budget__in=budgets,
            category=category
        ).aggregate(total=Sum('amount'))['total'] or 0

        spent = Expense.objects.filter(
            family=family,
            category=category,
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(total=Sum('amount'))['total'] or 0

        if planned > 0:
            category_performance.append({
                'category': category.name,
                'planned': float(planned),
                'spent': float(spent),
                'variance': float(planned - spent),
                'efficiency': (spent / planned) * 100 if planned > 0 else 0,
            })

    context = {
        'budget_data': budget_data,
        'category_performance': category_performance,
        'period': period,
    }

    return render(request, 'budgets/budget_analysis.html', context)