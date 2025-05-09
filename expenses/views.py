# expenses/views.py
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import json
import datetime
from django.db.models import Sum, Avg, Max, Count, F, Q
from django.db.models.functions import TruncMonth, TruncDay
from django.utils.timezone import localdate


from budgets.models import Budget, BudgetCategory, Category
from .models import Expense
from .forms import ExpenseForm


@login_required
def expense_list(request):
    family = request.user.family
    today = timezone.now().date()

    # Parameter aus GET
    period = request.GET.get('period', 'all')
    category_id = request.GET.get('category')
    sort = request.GET.get('sort', 'date_desc')

    # Basis-QuerySet
    expenses = Expense.objects.filter(family=family)

    # Zeitraumfilter
    if period == 'month':
        expenses = expenses.filter(date__year=today.year, date__month=today.month)
    elif period == 'last_month':
        last_month = (today.replace(day=1) - timezone.timedelta(days=1))
        expenses = expenses.filter(date__year=last_month.year, date__month=last_month.month)
    elif period == '3months':
        three_months_ago = today - timezone.timedelta(days=90)
        expenses = expenses.filter(date__gte=three_months_ago)
    elif period == 'year':
        expenses = expenses.filter(date__year=today.year)

    # Kategoriefilter
    if category_id:
        expenses = expenses.filter(category_id=category_id)

    # Sortierung
    if sort == 'date_asc':
        expenses = expenses.order_by('date')
    elif sort == 'amount_desc':
        expenses = expenses.order_by('-amount')
    elif sort == 'amount_asc':
        expenses = expenses.order_by('amount')
    else:  # default
        expenses = expenses.order_by('-date')

    # Gesamtbetrag berechnen
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0

    # Kategorienliste für Sidebar
    categories = Category.objects.all()

    context = {
        'expenses': expenses,
        'total_amount': total_amount,
        'categories': categories,
        'period': period,
        'category': category_id,
        'sort': sort
    }

    return render(request, 'expenses/expense_list.html', context)


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.family = request.user.family
            expense.user = request.user

            # Sicherstellen, dass immer ein Datum gesetzt ist
            if not expense.date:
                expense.date = timezone.now().date()

            expense.save()
            messages.success(request, 'Ausgabe erfolgreich hinzugefügt!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(initial={'date': localdate()})

    return render(request, 'expenses/add_expense.html', {'form': form})


@login_required
def expense_analysis(request):
    # Zeitraum aus Parameter holen oder Standard setzen
    period = request.GET.get('period', 'month')

    # Aktuelle Familie des Benutzers
    family = request.user.family

    # Aktuelles Datum
    today = timezone.now().date()

    # Zeitraum bestimmen
    if period == 'month':
        start_date = today.replace(day=1)
        end_date = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        period_name = f"{today.strftime('%B %Y')}"
        prev_start = (start_date - datetime.timedelta(days=1)).replace(day=1)
        prev_end = start_date
    elif period == 'last_month':
        end_date = today.replace(day=1)
        start_date = (end_date - datetime.timedelta(days=1)).replace(day=1)
        period_name = f"{start_date.strftime('%B %Y')}"
        prev_start = (start_date - datetime.timedelta(days=1)).replace(day=1)
        prev_end = start_date
    elif period == '3months':
        start_date = (today.replace(day=1) - datetime.timedelta(days=90))
        end_date = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        period_name = f"Letzte 3 Monate"
        prev_start = (start_date - datetime.timedelta(days=90))
        prev_end = start_date
    elif period == '6months':
        start_date = (today.replace(day=1) - datetime.timedelta(days=180))
        end_date = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        period_name = f"Letzte 6 Monate"
        prev_start = (start_date - datetime.timedelta(days=180))
        prev_end = start_date
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = (today.replace(month=12, day=31) + datetime.timedelta(days=1))
        period_name = f"{today.year}"
        prev_start = start_date.replace(year=today.year - 1)
        prev_end = end_date.replace(year=today.year - 1)
    else:  # Standardwert für ungültige Parameter
        start_date = today.replace(day=1)
        end_date = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        period_name = f"{today.strftime('%B %Y')}"
        prev_start = (start_date - datetime.timedelta(days=1)).replace(day=1)
        prev_end = start_date

    # Ausgaben im Zeitraum abfragen
    current_expenses = Expense.objects.filter(
        family=family,
        date__gte=start_date,
        date__lt=end_date
    )

    # Ausgaben im Vorherigen Zeitraum für Trendberechnung
    previous_expenses = Expense.objects.filter(
        family=family,
        date__gte=prev_start,
        date__lt=prev_end
    )

    # Gesamtausgaben berechnen
    total_expenses = current_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    previous_total = previous_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Trendberechnung (prozentuale Veränderung)
    if previous_total > 0:
        total_trend = ((total_expenses - previous_total) / previous_total) * 100
    else:
        total_trend = 0

    # Durchschnittliche Ausgaben pro Monat
    months_count = max(1, (end_date - start_date).days / 30)
    avg_per_month = total_expenses / months_count

    # Höchste Einzelausgabe
    highest_expense = current_expenses.aggregate(Max('amount'))['amount__max'] or 0
    expense_count = current_expenses.count()

    # Top 5 Ausgaben
    top_expenses = current_expenses.order_by('-amount')[:5]

    # Kategorienaufschlüsselung vorbereiten
    categories = Category.objects.all()
    category_breakdown = []

    # Farbzuordnungen für Kategorien (6 verschiedene Bootstrap-Farben)
    color_classes = ['primary', 'success', 'danger', 'warning', 'info', 'secondary', 'dark', 'primary']
    colors = ['0d6efd', '198754', 'dc3545', 'ffc107', '0dcaf0', '6c757d', '212529', '0d6efd']

    # Daten für Kategorien-Diagramm
    category_labels = []
    category_values = []
    category_total = 0

    # Icons für Kategorien (falls nicht in DB definiert)
    default_icons = {
        'Lebensmittel': 'cart',
        'Wohnen': 'house',
        'Transport': 'car-front',
        'Freizeit': 'controller',
        'Gesundheit': 'heart-pulse',
        'Bildung': 'book',
        'Kleidung': 'bag',
        'Sonstiges': 'three-dots'
    }

    # Kategorien mit Beträgen füllen
    for i, category in enumerate(categories):
        amount = current_expenses.filter(category=category).aggregate(Sum('amount'))['amount__sum'] or 0
        if amount > 0:
            category_total += amount

            # Vorperioden-Betrag für Trendberechnung
            prev_amount = previous_expenses.filter(category=category).aggregate(Sum('amount'))['amount__sum'] or 0
            if prev_amount > 0:
                trend = ((amount - prev_amount) / prev_amount) * 100
            else:
                trend = 0

            # Icon bestimmen
            icon = category.icon if hasattr(category, 'icon') and category.icon else default_icons.get(category.name,
                                                                                                       'tag')

            # Farbe rotieren
            color_index = i % len(color_classes)

            category_breakdown.append({
                'name': category.name,
                'amount': amount,
                'icon': icon,
                'color_class': color_classes[color_index],
                'color': colors[color_index],
                'trend': trend
            })

            # Für Diagrammdaten
            category_labels.append(category.name)
            category_values.append(float(amount))

    # Nach Betrag sortieren (absteigend)
    category_breakdown = sorted(category_breakdown, key=lambda x: x['amount'], reverse=True)

    # Prozentsätze berechnen
    for category in category_breakdown:
        category['percentage'] = (category['amount'] / total_expenses) * 100 if total_expenses > 0 else 0

    # Ausgabenverlauf für Diagramm vorbereiten
    if period in ['month', 'last_month']:
        # Tägliche Daten für Monatsansicht
        expenses_by_day = current_expenses.annotate(
            day=TruncDay('date')
        ).values('day').annotate(total=Sum('amount')).order_by('day')

        # Alle Tage im Monat erstellen (auch ohne Ausgaben)
        expense_trend_labels = []
        expense_trend_values = []

        current_date = start_date
        while current_date < end_date:
            expense_trend_labels.append(current_date.strftime('%d.%m'))

            # Betrag für diesen Tag suchen
            day_amount = 0
            for expense_day in expenses_by_day:
                if expense_day['day'].date() == current_date:
                    day_amount = float(expense_day['total'])
                    break

            expense_trend_values.append(day_amount)
            current_date += datetime.timedelta(days=1)
    else:
        # Monatliche Daten für längere Zeiträume
        expenses_by_month = current_expenses.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(total=Sum('amount')).order_by('month')

        expense_trend_labels = []
        expense_trend_values = []

        for expense_month in expenses_by_month:
            expense_trend_labels.append(expense_month['month'].strftime('%b %Y'))
            expense_trend_values.append(float(expense_month['total']))

    # JSON für die Diagramme
    expense_trend_data = json.dumps({
        'labels': expense_trend_labels,
        'values': expense_trend_values
    })

    category_data = json.dumps({
        'labels': category_labels,
        'values': category_values,
        'total': float(total_expenses)
    })

    # Finanzielle Erkenntnisse und Empfehlungen generieren
    insights = []

    # 1. Erkenntnis - Ausgabentrend
    if total_trend > 10:
        insights.append({
            'title': 'Steigende Ausgaben',
            'description': f'Deine Ausgaben sind im Vergleich zum vorherigen Zeitraum um {total_trend:.1f}% gestiegen.',
            'recommendation': 'Überprüfe, in welchen Kategorien die größten Steigerungen stattgefunden haben, und überlege dir Einsparmöglichkeiten.',
            'icon': 'graph-up-arrow',
            'type': 'warning'
        })
    elif total_trend < -10:
        insights.append({
            'title': 'Sinkende Ausgaben',
            'description': f'Gut gemacht! Deine Ausgaben sind im Vergleich zum vorherigen Zeitraum um {abs(total_trend):.1f}% gesunken.',
            'recommendation': 'Halte deine erfolgreichen Sparstrategien bei und setze dir weitere Ziele.',
            'icon': 'graph-down-arrow',
            'type': 'success'
        })

    # 2. Erkenntnis - Größte Kategorie
    if category_breakdown and category_breakdown[0]['percentage'] > 40:
        insights.append({
            'title': f'Hohe Ausgaben: {category_breakdown[0]["name"]}',
            'description': f'Die Kategorie "{category_breakdown[0]["name"]}" macht {category_breakdown[0]["percentage"]:.1f}% deiner Gesamtausgaben aus.',
            'recommendation': f'Untersuche genauer, wo du bei {category_breakdown[0]["name"]} einsparen könntest, um deine Ausgaben ausgewogener zu gestalten.',
            'icon': category_breakdown[0]['icon'],
            'type': 'info'
        })

    # 3. Erkenntnis - Ungewöhnlich hohe Einzelausgabe
    if highest_expense > avg_per_month * 0.5:
        insights.append({
            'title': 'Hohe Einzelausgabe',
            'description': f'Deine höchste Einzelausgabe im Zeitraum beträgt {highest_expense:.2f} CHF, was mehr als 50% deiner durchschnittlichen Monatsausgaben entspricht.',
            'recommendation': 'Prüfe, ob diese hohe Ausgabe geplant war oder ob du in Zukunft für solche Ausgaben besser vorsorgen solltest.',
            'icon': 'exclamation-triangle',
            'type': 'warning'
        })

    # 4. Erkenntnis - Sparpotential in einer Kategorie mit deutlichem Trend
    for category in category_breakdown:
        if category['trend'] > 20 and category['amount'] > avg_per_month * 0.2:
            insights.append({
                'title': f'Anstieg bei {category["name"]}',
                'description': f'Die Ausgaben für {category["name"]} sind um {category["trend"]:.1f}% gestiegen.',
                'recommendation': f'Überprüfe, warum die Kosten für {category["name"]} gestiegen sind, und identifiziere mögliche Einsparpotentiale.',
                'icon': category['icon'],
                'type': 'danger'
            })
            break

    # Auf maximal 3 Erkenntnisse beschränken
    insights = insights[:3]

    context = {
        'current_period': period_name,
        'current_period_param': period,
        'total_expenses': total_expenses,
        'total_trend': total_trend,
        'avg_per_month': avg_per_month,
        'highest_expense': highest_expense,
        'expense_count': expense_count,
        'category_breakdown': category_breakdown,
        'expense_trend_data': expense_trend_data,
        'category_data': category_data,
        'top_expenses': top_expenses,
        'insights': insights
    }

    return render(request, 'expenses/expense_analysis.html', context)


@login_required
def expense_detail(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, family=request.user.family)

    # Get budget category for this expense in the current month
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    next_month = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)

    try:
        current_budget = Budget.objects.get(
            family=request.user.family,
            month__gte=current_month_start,
            month__lt=next_month
        )

        # Get the budget category for this expense's category
        try:
            budget_category = BudgetCategory.objects.get(
                budget=current_budget,
                category=expense.category
            )

            # Calculate category expenses and remaining budget
            category_spent = Expense.objects.filter(
                family=request.user.family,
                category=expense.category,
                date__gte=current_month_start,
                date__lt=next_month
            ).aggregate(total=Sum('amount'))['total'] or 0

            category_remaining = budget_category.amount - category_spent

            if budget_category.amount > 0:
                category_percentage = (category_spent / budget_category.amount) * 100
            else:
                category_percentage = 0

        except BudgetCategory.DoesNotExist:
            budget_category = None
            category_spent = 0
            category_remaining = 0
            category_percentage = 0

    except Budget.DoesNotExist:
        current_budget = None
        budget_category = None
        category_spent = 0
        category_remaining = 0
        category_percentage = 0

    # Find similar expenses (same category, recent)
    similar_expenses = Expense.objects.filter(
        family=request.user.family,
        category=expense.category
    ).exclude(id=expense.id).order_by('-date')[:3]

    context = {
        'expense': expense,
        'current_budget': current_budget,
        'budget_category': budget_category,
        'category_spent': category_spent,
        'category_remaining': category_remaining,
        'category_percentage': min(category_percentage, 100),  # Cap at 100%
        'similar_expenses': similar_expenses,
    }

    return render(request, 'expenses/expense_detail.html', context)


@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, family=request.user.family)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ausgabe erfolgreich aktualisiert!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expenses/edit_expense.html', {'form': form, 'expense': expense})


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, family=request.user.family)

    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Ausgabe erfolgreich gelöscht!')
        return redirect('expense_list')

    return render(request, 'expenses/delete_expense.html', {'expense': expense})


@login_required
def expense_export(request):
    # Get query parameters
    export_format = request.GET.get('format', 'csv')
    period = request.GET.get('period', 'month')

    # Filter expenses based on period (similar to expense_analysis)
    # ... implement filtering logic ...

    if export_format == 'csv':
        # Generate CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

        # Create CSV writer and write data
        # ... implement CSV export ...

        return response

    elif export_format == 'pdf':
        # Generate PDF response
        # ... implement PDF export ...
        pass

    elif export_format == 'excel':
        # Generate Excel response
        # ... implement Excel export ...
        pass

    # Default fallback
    return redirect('expense_list')