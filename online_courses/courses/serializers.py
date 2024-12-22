from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review, Course, Enrollment

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'course', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        course = data.get('course')
        user = request.user

        if not Enrollment.objects.filter(user=user, course=course, status='active').exists():
            raise serializers.ValidationError("You must be enrolled in the course to leave a review.")

        if request.method == "POST" and Review.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError("You have already reviewed this course.")

        return data