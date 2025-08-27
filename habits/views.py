from django.contrib.auth.models import User
from rest_framework import generics, viewsets, permissions
from .serializers import UserSerializer, HabitSerializer, HabitLogSerializer
from .models import Habit, HabitLog
from datetime import data, timedelta

class LogHabitView(generics.CreateAPIView):
    serializer_class = HabitLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
       
        habit_pk = self.kwargs.get('habit_pk')
        
        habit = generics.get_object_or_404(Habit, pk=habit_pk, user=self.request.user)
        
        serializer.save(habit=habit)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    permission_classes = []



class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       
        return Habit.objects.filter(user=self.request.user)
    
class HabitStatsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Habit.objects.all()
    lookup_field = 'pk' 

    def get(self, request, *args, **kwargs):
        
        habit = self.get_object()
        if habit.user != request.user:
            return response.Response(
                {"detail": "You do not have permission to view these stats."},
                status=status.HTTP_403_FORBIDDEN
            )

        
        current_streak = 0 
        longest_streak = 0 
        
        data = {
            "habit_id": habit.id,
            "habit_name": habit.name,
            "habit_type": habit.habit_type,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
        }
        return response.Response(data, status=status.HTTP_200_OK)
    

class HabitStatsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Habit.objects.all()
    lookup_field = 'pk'

    def calculate_streaks(self, habit):
        # all logs for this habit, sorted from newest to oldest
        logs = habit.habitlog_set.order_by('-completion_date')
        if not logs:
            return 0, 0 
        log_dates = {log.completion_date for log in logs}
        
        #Calculate Longest Streak
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

        # To Calculate Current Streak 
        current_streak = 0
        today = date.today()
        
        # Check if there is a log for today or yesterday to start the streak
        if today in log_dates or (today - timedelta(days=1)) in log_dates:
            day_to_check = today
            # If today is not in logs, start checking from yesterday
            if today not in log_dates:
                day_to_check = today - timedelta(days=1)
            
            while day_to_check in log_dates:
                current_streak += 1
                day_to_check -= timedelta(days=1)
        
        return current_streak, longest_streak

    def get(self, request, *args, **kwargs):
        habit = self.get_object()
        if habit.user != request.user:
            return response.Response(
                {"detail": "You do not have permission to view these stats."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        
        if habit.habit_type == 'BUILD':
            current_streak, longest_streak = self.calculate_streaks(habit)
        else:
            
            current_streak = 0
            longest_streak = 0

        data = {
            "habit_id": habit.id,
            "habit_name": habit.name,
            "habit_type": habit.habit_type,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "logs": [log.completion_date for log in habit.habitlog_set.all()] 
        }
        return response.Response(data, status=status.HTTP_200_OK)
    


class HabitStatsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Habit.objects.all()
    lookup_field = 'pk'

    def calculate_build_streaks(self, habit):
        logs = habit.habitlog_set.order_by('-completion_date')
        if not logs:
            return 0, 0

        # Collect unique log dates
        log_dates = {log.completion_date for log in logs}
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

        # Count consecutive days up to today
        current_streak = 0
        today = date.today()
        if today in log_dates or (today - timedelta(days=1)) in log_dates:
            day_to_check = today if today in log_dates else today - timedelta(days=1)
            while day_to_check in log_dates:
                current_streak += 1
                day_to_check -= timedelta(days=1)
        
        return current_streak, longest_streak

    def calculate_quit_streaks(self, habit):
        logs = habit.habitlog_set.order_by('-completion_date')
        today = date.today()
        start_date = habit.created_at.date()

        if not logs:
            # No relapses yet
            current_streak = (today - start_date).days + 1
            return current_streak, current_streak

        log_dates = {log.completion_date for log in logs}
        last_relapse_date = logs.first().completion_date
        current_streak = (today - last_relapse_date).days

        # Find max days between relapses
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
        else:  # QUIT
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