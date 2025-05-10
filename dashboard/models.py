# Erweiterte Dashboard-Modelle - zu dashboard/models.py hinzufügen

from django.db import models
from users.models import CustomUser


class DashboardPreference(models.Model):
    """Benutzer-spezifische Dashboard-Einstellungen"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='dashboard_preference')
    show_budget_widget = models.BooleanField(default=True)
    show_savings_widget = models.BooleanField(default=True)
    show_expenses_widget = models.BooleanField(default=True)
    show_quick_actions = models.BooleanField(default=True)
    show_analytics_widget = models.BooleanField(default=True)
    default_period = models.CharField(
        max_length=20,
        choices=[
            ('week', 'Diese Woche'),
            ('month', 'Dieser Monat'),
            ('year', 'Dieses Jahr')
        ],
        default='month'
    )

    # Widget-Reihenfolge (JSON gespeichert)
    widget_order = models.JSONField(default=list)

    # Farb-Theme
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Hell'),
            ('dark', 'Dunkel'),
            ('auto', 'Automatisch'),
        ],
        default='light'
    )

    def __str__(self):
        return f"Dashboard-Einstellungen für {self.user.username}"

    def get_default_widget_order(self):
        """Gibt Standard-Reihenfolge der Widgets zurück"""
        return [
            'quick_actions',
            'budget_overview',
            'savings_progress',
            'recent_expenses',
            'analytics_summary',
        ]

    def save(self, *args, **kwargs):
        if not self.widget_order:
            self.widget_order = self.get_default_widget_order()
        super().save(*args, **kwargs)


class QuickAction(models.Model):
    """Schnellaktionen für das Dashboard"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='quick_actions')
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    url = models.CharField(max_length=200)
    description = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=7, default='#0d6efd')  # Hex color
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    use_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def increment_use_count(self):
        self.use_count += 1
        self.save()


class DashboardWidget(models.Model):
    """Konfiguierbare Dashboard-Widgets"""
    WIDGET_TYPES = [
        ('budget_summary', 'Budget-Zusammenfassung'),
        ('expense_chart', 'Ausgaben-Diagramm'),
        ('savings_progress', 'Spar-Fortschritt'),
        ('quick_stats', 'Schnelle Statistiken'),
        ('recent_transactions', 'Letzte Transaktionen'),
        ('goals_overview', 'Ziel-Übersicht'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='dashboard_widgets')
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPES)
    title = models.CharField(max_length=100)
    position = models.IntegerField(default=0)
    size = models.CharField(
        max_length=20,
        choices=[
            ('small', 'Klein'),
            ('medium', 'Mittel'),
            ('large', 'Groß'),
            ('full', 'Volle Breite'),
        ],
        default='medium'
    )
    settings = models.JSONField(default=dict)  # Widget-spezifische Einstellungen
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['position']

    def get_data(self):
        """Gibt Daten für das Widget zurück"""
        # Diese Methode wird in Views implementiert
        pass


class FavoriteItem(models.Model):
    """Favoriten für häufig verwendete Features"""
    ITEM_TYPES = [
        ('expense', 'Ausgabe'),
        ('category', 'Kategorie'),
        ('budget', 'Budget'),
        ('saving_goal', 'Sparziel'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    item_id = models.IntegerField()
    name = models.CharField(max_length=200)
    added_at = models.DateTimeField(auto_now_add=True)
    access_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'item_type', 'item_id']

    def increment_access_count(self):
        self.access_count += 1
        self.save()


class ShortcutKey(models.Model):
    """Benutzerdefinierte Tastenkürzel"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shortcuts')
    action = models.CharField(max_length=100)
    key_combination = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'key_combination']

    def __str__(self):
        return f"{self.key_combination} → {self.action}"