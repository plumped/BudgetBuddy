from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import datetime

from .models import Budget, BudgetCategory, Category
from .forms import BudgetForm, BudgetCategoryFormSet


@login_required
def budget_list(request):
    budgets = Budget.objects.filter(family=request.user.family).order_by('-month')
    return render(request, 'budgets/budget_list.html', {'budgets': budgets})


@login_required
def budget_detail(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, family=request.user.family)
    return render(request, 'budgets/budget_detail.html', {'budget': budget})


@login_required
def create_budget(request):
    # Prüfen, ob bereits ein Budget für den aktuellen Monat existiert
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
        # Kein existierendes Budget gefunden, also neu erstellen
        pass

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.family = request.user.family
            budget.save()

            # Formset für Budgetkategorien
            formset = BudgetCategoryFormSet(request.POST, instance=budget)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Budget erfolgreich erstellt!')
                return redirect('budget_list')
    else:
        form = BudgetForm()
        formset = BudgetCategoryFormSet()

    # Hole alle verfügbaren Kategorien für das Formular
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