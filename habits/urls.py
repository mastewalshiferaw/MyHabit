from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegisterView, HabitViewSet, LogHabitView, HabitStatsView, DashboardView

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('habits/<int:habit_pk>/log/', LogHabitView.as_view(), name='log_habit'),
    path('habits/<int:pk>/stats/', HabitStatsView.as_view(), name='habit_stats'),
    path('', include(router.urls)),


]

