from django.contrib.auth.models import User
from rest_framework import generics, viewsets, permissions, response, status
from rest_framework.views import APIView
from .serializers import UserSerializer, HabitSerializer, HabitLogSerializer
from .models import Habit, HabitLog
from datetime import date, timedelta

# --- User Registration View ---
class RegisterView(generics.CreateAPIView):
    """Allows new users to create an account."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to register


# --- Habit CRUD ViewSet ---
class HabitViewSet(viewsets.ModelViewSet):
    """Handles all Create, Retrieve, Update, and Delete (CRUD) operations for habits."""
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """This method ensures that a user can only see their own habits."""
        return Habit.objects.filter(user=self.request.user)


# --- Habit Logging View ---
class LogHabitView(generics.CreateAPIView):
    """Handles the creation of a new log entry for a specific habit."""
    serializer_class = HabitLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Associates the log with the correct habit, ensuring the user owns it."""
        habit_pk = self.kwargs.get('habit_pk')
        habit = generics.get_object_or_404(Habit, pk=habit_pk, user=self.request.user)
        serializer.save(habit=habit)


# --- DETAILED STATS VIEW ---
class HabitStatsView(generics.RetrieveAPIView):
    """Provides detailed statistics for a single habit, including streak calculations."""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Habit.objects.all()
    lookup_field = 'pk'

    def calculate_build_streaks(self, habit):
        """Calculates the current and longest streaks for a 'BUILD' type habit."""
        logs = habit.habitlog_set.order_by('-completion_date')
        if not logs:
            return 0, 0

        log_dates = {log.completion_date for log in logs}
        
        # Calculate the longest streak by finding the longest chain of consecutive days
        longest_streak = 0
        if log_dates:
            sorted_dates = sorted(list(log_dates))
            current_longest = 1
            for i in range(1, len(sorted_dates)):
                if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                    current_longest += 1
                else:
                    longest_streak = max(longest_streak, current_longest)
                    current_longest = 1
            longest_streak = max(longest_streak, current_longest)

        # Calculate the current streak by counting backwards from the most recent log
        current_streak = 0
        today = date.today()
        most_recent_log_date = logs.first().completion_date

        # A streak is only "current" if the last log was today or yesterday
        if most_recent_log_date == today or most_recent_log_date == (today - timedelta(days=1)):
            day_to_check = most_recent_log_date
            while day_to_check in log_dates:
                current_streak += 1
                day_to_check -= timedelta(days=1)
        
        return current_streak, longest_streak

    def calculate_quit_streaks(self, habit):
        """Calculates the current and longest 'clean' streaks for a 'QUIT' type habit."""
        today = date.today()
        start_date = habit.created_at.date()

        # Get all unique, sorted relapse dates
        relapse_dates = sorted(list(
            habit.habitlog_set.values_list('completion_date', flat=True).distinct()
        ))
        relapse_dates = [d for d in relapse_dates if d <= today] # Ignore future dates

        if not relapse_dates:
            # If there are no relapses, the streak is from creation day to today
            current_streak = (today - start_date).days + 1
            return current_streak, current_streak

        # Current streak is the number of days since the most recent relapse
        last_relapse_date = relapse_dates[-1]
        current_streak = (today - last_relapse_date).days

        # To find the longest streak, we find the biggest gap in a timeline of events
        timeline_dates = [start_date - timedelta(days=1)] + relapse_dates + [today]
        
        longest_streak = 0
        for i in range(1, len(timeline_dates)):
            gap = (timeline_dates[i] - timeline_dates[i-1]).days - 1
            if gap > longest_streak:
                longest_streak = gap

        return current_streak, longest_streak

    def get(self, request, *args, **kwargs):
        habit = self.get_object()
        if habit.user != request.user:
            return response.Response(
                {"detail": "You do not have permission to view these stats."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Call the correct calculation method based on the habit's type
        if habit.habit_type == 'BUILD':
            current_streak, longest_streak = self.calculate_build_streaks(habit)
        else: # 'QUIT'
            current_streak, longest_streak = self.calculate_quit_streaks(habit)

        data = {
            "habit_id": habit.id,
            "habit_name": habit.name,
            "habit_type": habit.habit_type,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "logs": [log.completion_date for log in habit.habitlog_set.order_by('completion_date')]
        }
        return response.Response(data, status=status.HTTP_200_OK)


# --- DASHBOARD VIEW ---
class DashboardView(APIView):
    """Provides a high-level summary of all of a user's habits."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_habits = Habit.objects.filter(user=request.user)
        stats_calculator = HabitStatsView()

        dashboard_data = []
        for habit in user_habits:
            # For the dashboard, we only need the current streak
            if habit.habit_type == 'BUILD':
                current_streak, _ = stats_calculator.calculate_build_streaks(habit)
            else: 
                current_streak, _ = stats_calculator.calculate_quit_streaks(habit)

            dashboard_data.append({
                "habit_id": habit.id,
                "habit_name": habit.name,
                "habit_type": habit.habit_type,
                "current_streak": current_streak,
            })
        
        return response.Response(dashboard_data, status=status.HTTP_200_OK)