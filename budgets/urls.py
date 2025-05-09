from django.urls import path
from . import views

urlpatterns = [
    path('', views.budget_list, name='budget_list'),
    path('create/', views.create_budget, name='create_budget'),
    path('<int:budget_id>/', views.budget_detail, name='budget_detail'),
    path('<int:budget_id>/edit/', views.edit_budget, name='edit_budget'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.create_category, name='create_category'),
]