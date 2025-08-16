from django.db import models

from django.contrib.auth.models import User

class Habit(models.Model):
    class HabitType(models.TextChoices):
        BUILD = 'BUILD', 'Build'
        QUIT = 'QUIT', 'Quit'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    habit_type = models.CharField(
        max_length=5,
        choices=HabitType.choices,
        default=HabitType.BUILD
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    completion_date = models.DateField()

    class Meta:
        #a user can only log a habit once per day
        unique_together = ('habit', 'completion_date')

    def __str__(self):
        return f"{self.habit.name} - {self.completion_date}"