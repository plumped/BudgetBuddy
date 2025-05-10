from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('add/', views.add_expense, name='add_expense'),
    path('<int:expense_id>/', views.expense_detail, name='expense_detail'),
    path('<int:expense_id>/edit/', views.edit_expense, name='edit_expense'),
    path('<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('analysis/', views.expense_analysis, name='expense_analysis'),
    path('bulk-action/', views.bulk_expense_action, name='bulk_expense_action'),
    path('templates/', views.expense_template_list, name='expense_template_list'),
    path('templates/create/', views.create_expense_template, name='create_expense_template'),
    path('recurring/', views.recurring_expense_list, name='recurring_expense_list'),
    path('recurring/create/', views.create_recurring_expense, name='create_recurring_expense'),
    path('split/', views.split_expense_list, name='split_expense_list'),
    path('split/create/', views.create_split_expense, name='create_split_expense'),
    path('approval/', views.expense_approval_list, name='expense_approval_list'),
    path('approval/<int:approval_id>/approve/', views.approve_expense, name='approve_expense'),
    path('approval/<int:approval_id>/reject/', views.reject_expense, name='reject_expense'),
]