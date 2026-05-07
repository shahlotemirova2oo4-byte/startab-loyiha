"""Foydalanuvchi va profil modellari."""
from django.contrib.auth.models import AbstractUser
from django.db import models


INDUSTRY_CHOICES = (
    ('it', 'IT'),
    ('marketing', 'Marketing'),
    ('education', "Ta'lim"),
    ('medicine', 'Tibbiyot'),
    ('agriculture', "Qishloq xo'jaligi"),
    ('energy', 'Energiya'),
    ('logistics', 'Logistika'),
    ('other', 'Boshqa'),
)


class User(AbstractUser):
    """Maxsus foydalanuvchi modeli — rol bilan."""

    ROLE_CHOICES = (
        ('startup', 'Startapchi'),
        ('investor', 'Investor'),
    )

    email = models.EmailField('Email', unique=True)
    role = models.CharField('Rol', max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField('Telefon', max_length=20, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_startup(self):
        return self.role == 'startup'

    @property
    def is_investor(self):
        return self.role == 'investor'

    def get_profile(self):
        if self.is_startup:
            return getattr(self, 'startup_profile', None)
        if self.is_investor:
            return getattr(self, 'investor_profile', None)
        return None


class StartupProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='startup_profile'
    )
    industry = models.CharField('Soha', max_length=20, choices=INDUSTRY_CHOICES, default='other')
    bio = models.TextField('Qisqa bio', blank=True)
    avatar = models.ImageField('Avatar', upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'Startapchi profili'
        verbose_name_plural = 'Startapchilar profillari'

    def __str__(self):
        return f"Startapchi: {self.user.username}"


class InvestorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='investor_profile'
    )
    company_name = models.CharField('Kompaniya nomi', max_length=150, blank=True)
    industries = models.CharField(
        'Sohalar (vergul bilan)', max_length=300, blank=True,
        help_text="Masalan: it, education, medicine"
    )
    budget_min = models.DecimalField(
        "Byudjet (min, so'm)", max_digits=15, decimal_places=2, default=0
    )
    budget_max = models.DecimalField(
        "Byudjet (max, so'm)", max_digits=15, decimal_places=2, default=0
    )
    bio = models.TextField('Qisqa bio', blank=True)
    avatar = models.ImageField('Avatar', upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'Investor profili'
        verbose_name_plural = 'Investorlar profillari'

    def __str__(self):
        return f"Investor: {self.user.username}"
