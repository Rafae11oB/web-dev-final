from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Category, Course, Enrollment, Lesson, Review,
    Payment, Quiz, QuizQuestion, UserProgress
)

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('is_student', 'is_instructor')}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Lesson)
admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(UserProgress)
