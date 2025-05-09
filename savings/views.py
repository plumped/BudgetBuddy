from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import SavingGoal, SavingTransaction
from .forms import SavingGoalForm, SavingTransactionForm


@login_required
def saving_goals_list(request):
    goals = SavingGoal.objects.filter(family=request.user.family).order_by('-created_at')
    return render(request, 'savings/goals_list.html', {'goals': goals})


@login_required
def saving_goal_detail(request, goal_id):
    goal = get_object_or_404(SavingGoal, id=goal_id, family=request.user.family)
    transactions = goal.transactions.all().order_by('-date')

    # Formular für neue Transaktion
    if request.method == 'POST':
        form = SavingTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.goal = goal
            transaction.user = request.user
            transaction.save()

            # Aktualisiere den aktuellen Betrag des Sparziels
            if transaction.transaction_type == 'DEPOSIT':
                goal.current_amount += transaction.amount
            else:  # WITHDRAWAL
                goal.current_amount = max(0, goal.current_amount - transaction.amount)
            goal.save()

            messages.success(request, 'Transaktion erfolgreich gespeichert!')
            return redirect('saving_goal_detail', goal_id=goal.id)
    else:
        form = SavingTransactionForm(initial={'date': timezone.now().date()})

    # Berechne Tage bis zum Zieldatum
    days_remaining = None
    if goal.target_date:
        delta = goal.target_date - timezone.now().date()
        days_remaining = max(0, delta.days)

    context = {
        'goal': goal,
        'transactions': transactions,
        'form': form,
        'days_remaining': days_remaining,
    }
    return render(request, 'savings/goal_detail.html', context)


@login_required
def create_saving_goal(request):
    if request.method == 'POST':
        form = SavingGoalForm(request.POST, request.FILES)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.family = request.user.family
            goal.creator = request.user
            goal.save()
            messages.success(request, 'Sparziel erfolgreich erstellt!')
            return redirect('saving_goals_list')
    else:
        form = SavingGoalForm()

    return render(request, 'savings/create_goal.html', {'form': form})


@login_required
def edit_saving_goal(request, goal_id):
    goal = get_object_or_404(SavingGoal, id=goal_id, family=request.user.family)

    if request.method == 'POST':
        form = SavingGoalForm(request.POST, request.FILES, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sparziel erfolgreich aktualisiert!')
            return redirect('saving_goals_list')
    else:
        form = SavingGoalForm(instance=goal)

    return render(request, 'savings/edit_goal.html', {'form': form, 'goal': goal})


@login_required
def delete_saving_goal(request, goal_id):
    goal = get_object_or_404(SavingGoal, id=goal_id, family=request.user.family)

    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Sparziel erfolgreich gelöscht!')
        return redirect('saving_goals_list')

    return render(request, 'savings/delete_goal.html', {'goal': goal})