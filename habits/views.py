from django.contrib.auth.models import User
from rest_framework import generics, viewsets, permissions
from .serializers import UserSerializer, HabitSerializer, HabitLogSerializer
from .models import Habit, HabitLog

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