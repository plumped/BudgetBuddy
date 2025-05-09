from django.db import models


# Dashboard app doesn't need its own models since it aggregates data from other apps
# If you need to store dashboard-specific preferences in the future, you could add them here

class DashboardPreference(models.Model):
    """
    Model to store user-specific dashboard preferences
    (This is optional and could be implemented later if needed)
    """
    from users.models import CustomUser

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='dashboard_preference')
    show_budget_widget = models.BooleanField(default=True)
    show_savings_widget = models.BooleanField(default=True)
    show_expenses_widget = models.BooleanField(default=True)
    default_period = models.CharField(
        max_length=20,
        choices=[
            ('week', 'Diese Woche'),
            ('month', 'Dieser Monat'),
            ('year', 'Dieses Jahr')
        ],
        default='month'
    )

    def __str__(self):
        return f"Dashboard-Einstellungen für {self.user.username}"