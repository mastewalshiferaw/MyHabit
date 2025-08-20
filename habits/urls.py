from django.urls import path, include
from .views import RegisterView, HabitViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
  path('auth/register/', RegisterView.as_view(), name='register'),
  path('', include(router.urls)),
]