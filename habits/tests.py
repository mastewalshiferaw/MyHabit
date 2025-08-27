from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Habit, HabitLog
from datetime import date, timedelta

class HabitStatsTests(APITestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
      
        self.build_habit = Habit.objects.create(
            user=self.user,
            name='Test Build Habit',
            habit_type='BUILD'
        )

    def test_no_logs_streak(self):
        """Test that a habit with no logs has a streak of 0."""
        response = self.client.get(f'/api/habits/{self.build_habit.id}/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_streak'], 0)
        self.assertEqual(response.data['longest_streak'], 0)
    
    def test_current_streak_build_habit(self):
      """Current streak should be 2 days."""
    
      today = date.today()
      yesterday = today - timedelta(days=1)
    
      HabitLog.objects.create(habit=self.build_habit, completion_date=yesterday)
      HabitLog.objects.create(habit=self.build_habit, completion_date=today)
    
      response = self.client.get(f'/api/habits/{self.build_habit.id}/stats/')
      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(response.data['current_streak'], 2)

def test_broken_streak_build_habit(self):
    """Missed day should break streak."""
    today = date.today()
    two_days_ago = today - timedelta(days=2)
    
    HabitLog.objects.create(habit=self.build_habit, completion_date=two_days_ago)
    HabitLog.objects.create(habit=self.build_habit, completion_date=today)
    
    response = self.client.get(f'/api/habits/{self.build_habit.id}/stats/')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['current_streak'], 1)
    self.assertEqual(response.data['longest_streak'], 1)

def test_longest_streak_build_habit(self):
    """Longest streak should be 3 days."""
    today = date.today()
    
    # Past 3-day streak
    HabitLog.objects.create(habit=self.build_habit, completion_date=today - timedelta(days=10))
    HabitLog.objects.create(habit=self.build_habit, completion_date=today - timedelta(days=9))
    HabitLog.objects.create(habit=self.build_habit, completion_date=today - timedelta(days=8))
    
    # Current 2-day streak
    HabitLog.objects.create(habit=self.build_habit, completion_date=today - timedelta(days=1))
    HabitLog.objects.create(habit=self.build_habit, completion_date=today)
    
    response = self.client.get(f'/api/habits/{self.build_habit.id}/stats/')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['current_streak'], 2)
    self.assertEqual(response.data['longest_streak'], 3)

def test_quit_habit_streak(self):
    """Streak since last relapse should be 5 days."""
    quit_habit = Habit.objects.create(
        user=self.user,
        name='Test Quit Habit',
        habit_type='QUIT',
        created_at=(date.today() - timedelta(days=10))
    )
    
    # Relapsed 5 days ago
    HabitLog.objects.create(habit=quit_habit, completion_date=(date.today() - timedelta(days=5)))

    response = self.client.get(f'/api/habits/{quit_habit.id}/stats/')
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data['current_streak'], 5)