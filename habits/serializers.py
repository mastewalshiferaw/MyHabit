from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Habit

class UserSerializer(serializers.ModelSerializer):
  #It defines how to create a new user and correctly hashes their password
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
        return user

class HabitSerializer(serializers.ModelSerializer):
   user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

   class Meta:
      model = Habit
      fields = ('id', 'user', 'name', 'description', 'habit_type', 'created_at')

      def create(self, validated_data):
         validated_data['user']=self.context['request'].user
         return super().create(validated_data)