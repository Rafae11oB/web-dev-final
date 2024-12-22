from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # User Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Course URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    
    # Lesson URLs
    path('courses/<int:course_id>/lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    
    # User Progress
    path('courses/<int:course_id>/progress/', views.user_progress, name='user_progress'),
    
    # Reviews
    path('courses/<int:course_id>/review/', views.add_review, name='add_review'),
    
    # Payments
    path('courses/<int:course_id>/payment/', views.make_payment, name='make_payment'),
    
    # Quiz URLs
    path('quizzes/', views.all_quizzes, name='all_quizzes'),  # Optional: List all quizzes
    path('quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quizzes/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    
    # Course-specific Quizzes
    path('courses/<int:course_id>/quizzes/', views.course_quizzes, name='course_quizzes'),
    
]
