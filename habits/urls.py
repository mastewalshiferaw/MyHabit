from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegisterView, HabitViewSet, LogHabitView

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    # This is the new URL for logging a habit
    path('habits/<int:habit_pk>/log/', LogHabitView.as_view(), name='log_habit'),
    path('', include(router.urls)),
]