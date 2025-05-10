from django.urls import path
from . import views

urlpatterns = [
    path('', views.saving_goals_list, name='saving_goals_list'),
    path('create/', views.create_saving_goal, name='create_saving_goal'),
    path('<int:goal_id>/', views.saving_goal_detail, name='saving_goal_detail'),
    path('<int:goal_id>/edit/', views.edit_saving_goal, name='edit_saving_goal'),
    path('<int:goal_id>/delete/', views.delete_saving_goal, name='delete_saving_goal'),
    path('categories/', views.saving_category_list, name='saving_category_list'),
    path('categories/create/', views.create_saving_category, name='create_saving_category'),
    path('milestones/<int:goal_id>/', views.saving_milestones, name='saving_milestones'),
    path('challenges/', views.saving_challenge_list, name='saving_challenge_list'),
    path('challenges/create/', views.create_saving_challenge, name='create_saving_challenge'),
    path('challenges/<int:challenge_id>/', views.saving_challenge_detail, name='saving_challenge_detail'),
    path('auto-save/', views.auto_save_settings, name='auto_save_settings'),
]