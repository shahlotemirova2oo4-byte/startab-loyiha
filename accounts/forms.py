"""Foydalanuvchi formalari."""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from .models import User, StartupProfile, InvestorProfile


BOOTSTRAP_INPUT = 'form-control'
BOOTSTRAP_SELECT = 'form-select'


def _bootstrap(fields, css_class=BOOTSTRAP_INPUT):
    """Yordamchi: barcha maydonlarga Bootstrap klassini qo'shish."""
    for f in fields.values():
        existing = f.widget.attrs.get('class', '')
        f.widget.attrs['class'] = (existing + ' ' + css_class).strip()


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Ism', max_length=30, required=True)
    last_name = forms.CharField(label='Familiya', max_length=30, required=True)
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(label='Telefon', max_length=20, required=False)
    role = forms.ChoiceField(label='Rol', choices=User.ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'role',
                  'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)
        # role - radio (bootstrapda checkbox/radio uchun boshqa class)
        self.fields['role'].widget.attrs['class'] = 'form-check-input'

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Bunday email allaqachon mavjud.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
            # Profilni yaratish
            if user.role == 'startup':
                StartupProfile.objects.create(user=user)
            else:
                InvestorProfile.objects.create(user=user)
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)


class StartupProfileForm(forms.ModelForm):
    class Meta:
        model = StartupProfile
        fields = ('industry', 'bio', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = BOOTSTRAP_SELECT
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['class'] = BOOTSTRAP_INPUT
            else:
                field.widget.attrs['class'] = BOOTSTRAP_INPUT


class InvestorProfileForm(forms.ModelForm):
    class Meta:
        model = InvestorProfile
        fields = ('company_name', 'industries', 'budget_min', 'budget_max', 'bio', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = BOOTSTRAP_SELECT
            else:
                field.widget.attrs['class'] = BOOTSTRAP_INPUT


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)
