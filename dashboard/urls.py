from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('customize/', views.customize_dashboard, name='customize_dashboard'),
    path('widgets/', views.widget_settings, name='widget_settings'),
    path('quick-actions/', views.quick_action_settings, name='quick_action_settings'),
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('shortcuts/', views.shortcut_settings, name='shortcut_settings'),
]