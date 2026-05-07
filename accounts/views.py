"""Accounts viewlari: register, login, logout, profile."""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import (
    RegisterForm, LoginForm, StartupProfileForm,
    InvestorProfileForm, UserUpdateForm,
)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('ideas:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Xush kelibsiz, {user.first_name}! Ro'yxatdan o'tish muvaffaqiyatli yakunlandi."
            )
            return redirect('accounts:profile')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Xush kelibsiz, {form.get_user().first_name or form.get_user().username}!")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = 'ideas:home'


@login_required
def profile_view(request):
    user = request.user
    profile = user.get_profile()

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        if user.is_startup:
            profile_form = StartupProfileForm(request.POST, request.FILES, instance=profile)
        else:
            profile_form = InvestorProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profil maʼlumotlari yangilandi.')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        if user.is_startup:
            profile_form = StartupProfileForm(instance=profile)
        else:
            profile_form = InvestorProfileForm(instance=profile)

    # Statistika startapchi uchun
    stats = {}
    if user.is_startup:
        ideas_qs = user.ideas.all()
        stats['total_ideas'] = ideas_qs.count()
        stats['funded_ideas'] = ideas_qs.filter(status='funded').count()
        stats['total_offers'] = sum(idea.offers.count() for idea in ideas_qs)
    elif user.is_investor:
        offers_qs = user.offers_made.all()
        stats['total_offers'] = offers_qs.count()
        stats['accepted_offers'] = offers_qs.filter(status='accepted').count()
        stats['saved_count'] = user.saved_ideas.count()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
        'stats': stats,
    }
    return render(request, 'accounts/profile.html', context)
