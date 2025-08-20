from django.contrib.auth.models import User
from rest_framework import generics, viewsets, permissions
from .serializers import UserSerializer, HabitSerializer
from .models import Habit


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [] # No permission needed to register

class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    # only authenticated users can access these endpoints
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        #filter habits by the currently logged-in user
        return Habit.objects.filter(user=self.request.user)