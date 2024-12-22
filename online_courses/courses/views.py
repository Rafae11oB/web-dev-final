from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, Category, Enrollment, Lesson, Review, UserProgress, Payment, Quiz, QuizQuestion
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm, ReviewForm, PaymentForm, QuizForm
from django.contrib import messages

def home(request):
    categories = Category.objects.all()
    courses = Course.objects.all()[:5]  # Display latest 5 courses
    return render(request, 'courses/home.html', {'categories': categories, 'courses': courses})

def course_list(request):
    courses = Course.objects.all()
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    if category_id:
        courses = courses.filter(category_id=category_id)
    return render(request, 'courses/course_list.html', {'courses': courses, 'categories': categories})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    quizzes = course.quizzes.all()
    reviews_list = course.reviews.order_by('-created_at')
    
    # Pagination for reviews (optional)
    from django.core.paginator import Paginator
    paginator = Paginator(reviews_list, 5)  # Show 5 reviews per page
    page_number = request.GET.get('page')
    reviews = paginator.get_page(page_number)
    
    # Check if the user is enrolled in the course
    is_enrolled = False
    has_reviewed = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=course,
            status='active'
        ).exists()
        
        # Check if the user has already reviewed the course
        has_reviewed = Review.objects.filter(
            user=request.user,
            course=course
        ).exists()
    
    context = {
        'course': course,
        'lessons': lessons,
        'quizzes': quizzes,
        'reviews': reviews,
        'is_enrolled': is_enrolled,          # Pass the enrollment flag
        'has_reviewed': has_reviewed,        # Pass the review flag
    }
    return render(request, 'courses/course_detail.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally, assign student or instructor status
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'courses/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'courses/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    return redirect('course_detail', course_id=course_id)

@login_required
def lesson_detail(request, course_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id)
    enrollment = Enrollment.objects.filter(user=request.user, course_id=course_id, status='active').first()
    if not enrollment:
        return redirect('course_detail', course_id=course_id)
    
    # Mark lesson as completed
    progress, created = UserProgress.objects.get_or_create(user=request.user, course_id=course_id)
    progress.completed_lessons.add(lesson)
    progress.save()

    return render(request, 'courses/lesson_detail.html', {'lesson': lesson})

@login_required
def user_progress(request, course_id):
    progress = get_object_or_404(UserProgress, user=request.user, course_id=course_id)
    return render(request, 'courses/user_progress.html', {'progress': progress})

@login_required
def add_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                course=course,
                user=request.user,
                rating=form.cleaned_data['rating'],
                comment=form.cleaned_data['comment']
            )
            return redirect('course_detail', course_id=course_id)
    else:
        form = ReviewForm()
    return render(request, 'courses/add_review.html', {'form': form, 'course': course})

@login_required
def make_payment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            Payment.objects.create(
                user=request.user,
                amount=course.price,
                status='completed'  # In real scenarios, set based on payment gateway response
            )
            Enrollment.objects.create(user=request.user, course=course, status='active')
            return redirect('course_detail', course_id=course_id)
    else:
        form = PaymentForm(initial={'amount': course.price})
    return render(request, 'courses/make_payment.html', {'form': form, 'course': course})

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course
    
    # Check if user is enrolled in the course
    if not Enrollment.objects.filter(user=request.user, course=course, status='active').exists():
        messages.error(request, 'You must be enrolled in the course to take this quiz.')
        return redirect('course_detail', course_id=course.id)
    
    questions = QuizQuestion.objects.filter(quiz=quiz)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, questions=questions)
        if form.is_valid():
            score = 0
            for question in questions:
                selected_option = form.cleaned_data.get(f'question_{question.id}')
                if selected_option == question.correct_option:
                    score += 1
            
            # Update or create UserProgress
            progress, created = UserProgress.objects.get_or_create(user=request.user, course=course)
            progress.quiz_scores[str(quiz.id)] = score  # Assuming quiz.id is unique
            progress.save()
            
            messages.success(request, f'You scored {score} out of {quiz.total_marks}.')
            return redirect('quiz_result', quiz_id=quiz.id)
    else:
        form = QuizForm(questions=questions)
    
    context = {
        'quiz': quiz,
        'form': form,
        'questions': questions
    }
    return render(request, 'courses/take_quiz.html', context)

@login_required
def all_quizzes(request):
    """
    Display all quizzes across all courses.
    Accessible only to authenticated users.
    """
    quizzes = Quiz.objects.select_related('course').all()
    context = {
        'quizzes': quizzes
    }
    return render(request, 'courses/all_quizzes.html', context)

@login_required
def quiz_detail(request, quiz_id):
    """
    Display details of a specific quiz, including its questions.
    Accessible only to authenticated users enrolled in the associated course.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = QuizQuestion.objects.filter(quiz=quiz)
    
    # Optional: Check if the user is enrolled in the course
    if not request.user.enrollments.filter(course=quiz.course, status='active').exists():
        # Optionally, redirect to enrollment page or show a message
        return render(request, 'courses/access_denied.html', {'message': 'You are not enrolled in this course.'})
    
    context = {
        'quiz': quiz,
        'questions': questions
    }
    return render(request, 'courses/quiz_detail.html', context)

@login_required
def course_quizzes(request, course_id):
    """
    Display all quizzes for a specific course.
    Accessible only to authenticated users enrolled in the course.
    """
    course = get_object_or_404(Course, id=course_id)
    quizzes = course.quizzes.all()
    
    # Optional: Check if the user is enrolled in the course
    if not request.user.enrollments.filter(course=course, status='active').exists():
        # Optionally, redirect to enrollment page or show a message
        return render(request, 'courses/access_denied.html', {'message': 'You are not enrolled in this course.'})
    
    context = {
        'course': course,
        'quizzes': quizzes
    }
    return render(request, 'courses/course_quizzes.html', context)

@login_required
def quiz_result(request, quiz_id):
    """
    Displays the user's result for a specific quiz.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course
    
    # Retrieve user's score from UserProgress
    try:
        progress = UserProgress.objects.get(user=request.user, course=course)
        score = progress.quiz_scores.get(str(quiz.id), 0)
    except UserProgress.DoesNotExist:
        score = 0  # Default score if not found
    
    context = {
        'quiz': quiz,
        'score': score,
        'total': quiz.total_marks
    }
    return render(request, 'courses/quiz_result.html', context)