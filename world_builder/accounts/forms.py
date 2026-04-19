from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordChangeForm

from accounts.models import Profile

UserModel = get_user_model()



class UserBaseForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['email', 'username']
        labels = {
            'email': 'Email Address',
            'username': 'Username',
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'name@example.com',
                'class': 'form-control'
            }),
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a username',
                'class': 'form-control'
            }),
        }
        help_texts = {
            'username': 'Visible to others on your creations.',
            'email': 'Used for login. We value your privacy.'
        }
        error_messages = {
            'email': {
                'required': 'Enter an email address.',
                'unique': 'This email is already in use. Try logging in?',
                'invalid': 'Enter a valid email address.',
            },
            'username': {
                'required': 'Enter a username.',
                'unique': 'This username is taken. Try another?',
                'max_length': 'Username must be 100 characters or fewer.',
            }
        }

class UserRegisterForm(UserBaseForm, UserCreationForm):
    class Meta(UserBaseForm.Meta):
        fields = ['email', 'username', 'password1', 'password2']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })

        self.fields['password1'].error_messages.update({
            'required': 'Enter a password.'
        })
        self.fields['password2'].error_messages.update({
            'required': 'Confirm your password.'
        })

class UserUpdateForm(UserBaseForm, UserChangeForm):
    password = None
    class Meta(UserBaseForm.Meta):
        pass




class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email Address'
        self.fields['password'].label = 'Password'

        self.fields['username'].widget.attrs.update({
            'placeholder': 'e.g., writer@example.com',
            'class': 'form-control'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control'
        })

        self.fields['username'].error_messages.update({
            'required': 'Email address is required.'
        })
        self.fields['password'].error_messages.update({
            'required': 'Password is required.'
        })


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["owner"]
        labels = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'description': 'About you',
            'date_of_birth': 'Date of birth',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last name',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Location'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Tell us about yourself...',
                'rows': 3
            }),
        }
        error_messages = {
            'first_name': {
                'max_length': 'First name cannot exceed 50 characters.'
            },
            'last_name': {
                'max_length': 'Last name cannot exceed 50 characters.'
            },
            'location': {
                'max_length': 'Location cannot exceed 50 characters.'
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Current Password'
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'Confirm New Password'

        self.fields['old_password'].help_text = 'Enter your current password to confirm changes.'

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })


class UserDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I understand that deleting my account is permanent and cannot be undone.",
        error_messages={
            'required': 'You must confirm before deleting your account.'
        }
    )