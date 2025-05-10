from django.urls import path
from . import views

urlpatterns = [
    path('', views.budget_list, name='budget_list'),
    path('create/', views.create_budget, name='create_budget'),
    path('<int:budget_id>/', views.budget_detail, name='budget_detail'),
    path('<int:budget_id>/edit/', views.edit_budget, name='edit_budget'),
    path('<int:budget_id>/copy/', views.copy_budget, name='copy_budget'),
    path('analysis/', views.budget_analysis, name='budget_analysis'),
    path('templates/', views.budget_template_list, name='budget_template_list'),
    path('templates/create/', views.create_budget_template, name='create_budget_template'),
    path('templates/<int:template_id>/edit/', views.edit_budget_template, name='edit_budget_template'),
    path('templates/<int:template_id>/delete/', views.delete_budget_template, name='delete_budget_template'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
]