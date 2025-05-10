from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import datetime

from .models import Budget, BudgetCategory, Category
from .forms import BudgetForm, BudgetCategoryFormSet
from django.shortcuts import render, get_object_or_404
from expenses.models import Expense
from .models import Budget
import json


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

    context = {
        'budgets': budgets,
        'current_budget': current_budget,
        'categories_count': categories_count
    }

    return render(request, 'budgets/budget_list.html', context)


@login_required
def budget_detail(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, family=request.user.family)

    # Kategorien-Daten für Tabelle
    budget_categories = []
    for bc in budget.categories.select_related('category'):
        spent = Expense.objects.filter(
            family=budget.family,
            category=bc.category,
            date__year=budget.month.year,
            date__month=budget.month.month
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        remaining = bc.amount - spent
        percentage = (spent / bc.amount * 100) if bc.amount > 0 else 0

        budget_categories.append({
            'name': bc.category.name,
            'icon': bc.category.icon,
            'budget': bc.amount,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage
        })

    # Chart-Daten vorbereiten
    chart_data = {
        'labels': [cat['name'] for cat in budget_categories],
        'values': [float(cat['spent']) for cat in budget_categories],
        'total': float(sum(cat['spent'] for cat in budget_categories))
    }

    # Letzte Ausgaben im Monat
    recent_expenses = Expense.objects.filter(
        family=budget.family,
        date__year=budget.month.year,
        date__month=budget.month.month
    ).select_related('category').order_by('-date')[:10]

    context = {
        'budget': budget,
        'budget_categories': budget_categories,
        'total_spent': budget.total_spent,
        'budget_remaining': budget.remaining_amount,
        'chart_data': json.dumps(chart_data),
        'recent_expenses': recent_expenses
    }

    return render(request, 'budgets/budget_detail.html', context)


@login_required
def create_budget(request):
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    next_month = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)

    try:
        existing_budget = Budget.objects.get(
            family=request.user.family,
            month__gte=current_month_start,
            month__lt=next_month
        )
        return redirect('edit_budget', budget_id=existing_budget.id)
    except Budget.DoesNotExist:
        pass

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        formset = BudgetCategoryFormSet(request.POST)  # <-- IMMER initialisieren

        if form.is_valid():
            budget = form.save(commit=False)
            budget.family = request.user.family
            budget.save()

            formset = BudgetCategoryFormSet(request.POST, instance=budget)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Budget erfolgreich erstellt!')
                return redirect('budget_list')
    else:
        form = BudgetForm()
        formset = BudgetCategoryFormSet()

    categories = Category.objects.all()

    context = {
        'form': form,
        'formset': formset,
        'categories': categories,
    }
    return render(request, 'budgets/create_budget.html', context)



@login_required
def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, family=request.user.family)

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()

            # Formset für Budgetkategorien
            formset = BudgetCategoryFormSet(request.POST, instance=budget)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Budget erfolgreich aktualisiert!')
                return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget)
        formset = BudgetCategoryFormSet(instance=budget)

    context = {
        'form': form,
        'formset': formset,
        'budget': budget,
    }
    return render(request, 'budgets/edit_budget.html', context)


@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'budgets/category_list.html', {'categories': categories})


@login_required
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.POST.get('icon')

        if name:
            Category.objects.create(name=name, icon=icon or 'tag')
            messages.success(request, 'Kategorie erfolgreich erstellt!')
            return redirect('category_list')

    # Icons-Liste für die Auswahl
    icons = [
        'cart', 'house', 'car-front', 'controller', 'heart-pulse',
        'book', 'bag', 'piggy-bank', 'cash', 'tags', 'gift',
        'cup-hot', 'phone', 'briefcase', 'bank', 'tools',
        'emoji-smile', 'globe', 'music-note', 'lamp', 'scissors'
    ]

    return render(request, 'budgets/create_category.html', {'icons': icons})


@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.POST.get('icon')

        if name:
            category.name = name
            category.icon = icon
            category.save()
            messages.success(request, 'Kategorie erfolgreich aktualisiert!')

        return redirect('category_list')

    return redirect('category_list')


@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        # Kategorie löschen
        # Hinweis: In einem realen System würde man eventuell die verknüpften Ausgaben einer Standardkategorie zuordnen
        category.delete()
        messages.success(request, 'Kategorie erfolgreich gelöscht!')

    return redirect('category_list')