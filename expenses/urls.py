from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('add/', views.add_expense, name='add_expense'),
    path('<int:expense_id>/', views.expense_detail, name='expense_detail'),
    path('<int:expense_id>/edit/', views.edit_expense, name='edit_expense'),
    path('<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),
    path('analysis/', views.expense_analysis, name='expense_analysis'),
]