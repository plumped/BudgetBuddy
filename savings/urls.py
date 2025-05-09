from django.urls import path
from . import views

urlpatterns = [
    path('', views.saving_goals_list, name='saving_goals_list'),
    path('create/', views.create_saving_goal, name='create_saving_goal'),
    path('<int:goal_id>/', views.saving_goal_detail, name='saving_goal_detail'),
    path('<int:goal_id>/edit/', views.edit_saving_goal, name='edit_saving_goal'),
    path('<int:goal_id>/delete/', views.delete_saving_goal, name='delete_saving_goal'),
]