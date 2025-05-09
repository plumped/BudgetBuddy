# BudgetBuddy/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/'), name='home'),
    path('dashboard/', include('dashboard.urls')),
    path('users/', include('users.urls')),
    path('budgets/', include('budgets.urls')),
    path('expenses/', include('expenses.urls')),
    path('savings/', include('savings.urls')),

    # Django auth views for password reset
    path('password-reset/',
         include('django.contrib.auth.urls')),
]

# Für Medien während der Entwicklung hinzufügen
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)