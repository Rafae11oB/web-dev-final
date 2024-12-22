from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_student = forms.BooleanField(required=False)
    is_instructor = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'is_student', 'is_instructor', 'password1', 'password2')

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ReviewForm(forms.Form):
    rating = forms.IntegerField(min_value=1, max_value=5)
    comment = forms.CharField(widget=forms.Textarea)

class PaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, disabled=False)

class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(QuizForm, self).__init__(*args, **kwargs)
        for question in questions:
            choices = [
                ('A', 'A. ' + question.option_a),
                ('B', 'B. ' + question.option_b),
                ('C', 'C. ' + question.option_c),
                ('D', 'D. ' + question.option_d),
            ]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.question_text,
                choices=choices,
                widget=forms.RadioSelect,
                required=True
            )