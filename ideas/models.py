"""G'oyalar, takliflar, saqlangan g'oyalar va xabarlar."""
from django.conf import settings
from django.db import models
from django.urls import reverse


REGION_CHOICES = (
    ('toshkent_sh', 'Toshkent shahri'),
    ('toshkent_v', 'Toshkent viloyati'),
    ('andijon', 'Andijon'),
    ('buxoro', 'Buxoro'),
    ('fargona', "Farg'ona"),
    ('jizzax', 'Jizzax'),
    ('xorazm', 'Xorazm'),
    ('namangan', 'Namangan'),
    ('navoiy', 'Navoiy'),
    ('qashqadaryo', 'Qashqadaryo'),
    ('qoraqalpogiston', "Qoraqalpog'iston"),
    ('samarqand', 'Samarqand'),
    ('sirdaryo', 'Sirdaryo'),
    ('surxondaryo', 'Surxondaryo'),
)


# Sohalar (accounts/models.py dagi bilan bir xil bo'lishi uchun import qilamiz)
def get_industry_choices():
    from accounts.models import INDUSTRY_CHOICES
    return INDUSTRY_CHOICES


class Idea(models.Model):
    STATUS_CHOICES = (
        ('new', 'Yangi'),
        ('funded', 'Moliyalashtirilgan'),
        ('closed', 'Yopiq'),
    )

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

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ideas',
        verbose_name='Muallif'
    )
    title = models.CharField('Sarlavha', max_length=200)
    short_description = models.CharField('Qisqa tavsif', max_length=300)
    description = models.TextField('Batafsil tavsif')
    needed_amount = models.DecimalField(
        "Kerakli mablag' (so'm)", max_digits=15, decimal_places=2
    )
    equity_percent = models.DecimalField(
        'Ulush (%)', max_digits=5, decimal_places=2,
        help_text='0 dan 100 gacha'
    )
    industry = models.CharField('Soha', max_length=20, choices=INDUSTRY_CHOICES)
    region = models.CharField('Hudud', max_length=30, choices=REGION_CHOICES)
    file = models.FileField(
        'Rasm yoki PDF', upload_to='ideas/', blank=True, null=True,
        help_text="JPG, PNG yoki PDF (max 10 MB)"
    )
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "G'oya"
        verbose_name_plural = "G'oyalar"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ideas:detail', kwargs={'pk': self.pk})

    @property
    def is_image(self):
        if not self.file:
            return False
        name = self.file.name.lower()
        return name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))

    @property
    def is_pdf(self):
        return self.file and self.file.name.lower().endswith('.pdf')

    @property
    def offers_count(self):
        return self.offers.count()

    @property
    def is_open(self):
        return self.status == 'new'


class Offer(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('accepted', 'Qabul qilingan'),
        ('rejected', 'Rad etilgan'),
    )

    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='offers',
                             verbose_name="G'oya")
    investor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers_made',
        verbose_name='Investor'
    )
    amount = models.DecimalField("Taklif qilingan mablag' (so'm)", max_digits=15, decimal_places=2)
    equity_percent = models.DecimalField('Ulush (%)', max_digits=5, decimal_places=2)
    message = models.TextField('Xabar', blank=True)
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Taklif'
        verbose_name_plural = 'Takliflar'

    def __str__(self):
        return f"{self.investor.username} → {self.idea.title} ({self.get_status_display()})"


class SavedIdea(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_ideas',
        verbose_name='Foydalanuvchi'
    )
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='saved_by',
                             verbose_name="G'oya")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'idea')
        ordering = ('-created_at',)
        verbose_name = "Saqlangan g'oya"
        verbose_name_plural = "Saqlangan g'oyalar"

    def __str__(self):
        return f"{self.user.username} ❤ {self.idea.title}"


class Message(models.Model):
    """Taklifga biriktirilgan xabar."""
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='messages',
                              verbose_name='Taklif')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages',
        verbose_name='Yuboruvchi'
    )
    content = models.TextField('Matn')
    is_read = models.BooleanField("Ko'rilgan", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Xabar'
        verbose_name_plural = 'Xabarlar'

    def __str__(self):
        return f"{self.sender.username}: {self.content[:40]}"
