from django.contrib.auth.models import User
from rest_framework import generics, viewsets, permissions, response, status
from rest_framework.views import APIView
from .serializers import UserSerializer, HabitSerializer, HabitLogSerializer
from .models import Habit, HabitLog
from datetime import date, timedelta

# --- User Registration View ---
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []


# --- Habit CRUD ViewSet ---
class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


# --- Habit Logging View ---
class LogHabitView(generics.CreateAPIView):
    serializer_class = HabitLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        habit_pk = self.kwargs.get('habit_pk')
        habit = generics.get_object_or_404(Habit, pk=habit_pk, user=self.request.user)
        serializer.save(habit=habit)


# --- DETAILED STATS VIEW ---
class HabitStatsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Habit.objects.all()
    lookup_field = 'pk'

    def calculate_build_streaks(self, habit):
        logs = habit.habitlog_set.order_by('-completion_date')
        if not logs:
            return 0, 0

        log_dates = {log.completion_date for log in logs}
        
        # Longest Streak Calculation
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

        # Current Streak Calculation
        current_streak = 0
        today = date.today()
        most_recent_log_date = logs.first().completion_date

        if most_recent_log_date == today or most_recent_log_date == (today - timedelta(days=1)):
            day_to_check = most_recent_log_date
            while day_to_check in log_dates:
                current_streak += 1
                day_to_check -= timedelta(days=1)
        
        return current_streak, longest_streak

    def calculate_quit_streaks(self, habit):
        logs = habit.habitlog_set.order_by('-completion_date')
        today = date.today()
        start_date = habit.created_at.date()

        if not logs:
            current_streak = (today - start_date).days + 1
            return current_streak, current_streak

        log_dates = {log.completion_date for log in logs}
        last_relapse_date = logs.first().completion_date
        current_streak = (today - last_relapse_date).days

        sorted_dates = sorted(list(log_dates))
        longest_streak = 0
        
        if sorted_dates:
            longest_streak = max(longest_streak, (sorted_dates[0] - start_date).days)
        
        for i in range(1, len(sorted_dates)):
            gap = (sorted_dates[i] - sorted_dates[i-1]).days - 1
            longest_streak = max(longest_streak, gap)

        longest_streak = max(longest_streak, current_streak)
        return current_streak, longest_streak

    def get(self, request, *args, **kwargs):
        habit = self.get_object()
        if habit.user != request.user:
            return response.Response(
                {"detail": "You do not have permission to view these stats."},
                status=status.HTTP_403_FORBIDDEN
            )
        
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_habits = Habit.objects.filter(user=request.user)
        stats_calculator = HabitStatsView()

        dashboard_data = []
        for habit in user_habits:
            if habit.habit_type == 'BUILD':
                current_streak, _ = stats_calculator.calculate_build_streaks(habit)
            else: # 'QUIT
                current_streak, _ = stats_calculator.calculate_quit_streaks(habit)

            dashboard_data.append({
                "habit_id": habit.id,
                "habit_name": habit.name,
                "habit_type": habit.habit_type,
                "current_streak": current_streak,
            })
        
        return response.Response(dashboard_data, status=status.HTTP_200_OK)