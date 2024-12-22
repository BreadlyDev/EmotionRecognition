from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'login__input',
            'placeholder': 'Email',
            'required': 'required'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'login__input',
            'placeholder': 'Password',
            'required': 'required'
        })
    )
    photo = forms.ImageField(
        widget=forms.HiddenInput(attrs={
            'id': 'photoInput'
        }),
        required=False
    )

class RegisterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'register__input',
            'placeholder': 'Email',
            'required': 'required'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'register__input',
            'placeholder': 'Password',
            'required': 'required'
        })
    )
    photo = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'photo-input',
            'id': 'photoInput'
        }),
        required=False
    )
