from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Habit, HabitLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')
        
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )

        user.set_password(validated_data["password"])  
        user.save()
        return user


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Habit
        fields = ('id', 'user', 'name', 'description', 'habit_type', 'created_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ('id', 'habit', 'completion_date')
        read_only_fields = ('habit',)