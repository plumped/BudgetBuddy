from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('family/', views.family_view, name='family'),
    path('family/add-member/', views.add_family_member, name='add_family_member'),
    path('family/remove-member/<int:member_id>/', views.remove_family_member, name='remove_family_member'),
    path('family/settings/', views.family_settings, name='family_settings'),
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/create/', views.create_account, name='create_account'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/settings/', views.notification_settings, name='notification_settings'),
    path('personal-budget/', views.personal_budget_settings, name='personal_budget_settings'),
]