"""Test ma'lumotlarini yaratish: 2 startapchi, 2 investor, 3 g'oya, 2 taklif, 1 muvaffaqiyat."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import StartupProfile, InvestorProfile
from ideas.models import Idea, Offer, Message, SavedIdea


User = get_user_model()


class Command(BaseCommand):
    help = "Loyihani test ma'lumotlari bilan to'ldiradi."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Mavjud test ma'lumotlari tozalanmoqda..."))

        # Faqat seed foydalanuvchilarni o'chiramiz (superuserga tegmaymiz)
        seed_usernames = ['startup_aziz', 'startup_dilnoza', 'investor_olim', 'investor_madina']
        User.objects.filter(username__in=seed_usernames).delete()

        self.stdout.write(self.style.WARNING("Test foydalanuvchilar yaratilmoqda..."))

        # ---- Startapchilar ----
        s1 = User.objects.create_user(
            username='startup_aziz', email='aziz@example.com', password='parol12345',
            first_name='Aziz', last_name='Karimov', role='startup', phone='+998901112233',
        )
        StartupProfile.objects.create(user=s1, industry='it', bio="IT sohasida 5 yillik tajriba.")

        s2 = User.objects.create_user(
            username='startup_dilnoza', email='dilnoza@example.com', password='parol12345',
            first_name='Dilnoza', last_name='Toshmatova', role='startup', phone='+998904445566',
        )
        StartupProfile.objects.create(user=s2, industry='education', bio="Ta'lim texnologiyalari ishqibozi.")

        # ---- Investorlar ----
        i1 = User.objects.create_user(
            username='investor_olim', email='olim@example.com', password='parol12345',
            first_name='Olim', last_name='Yusupov', role='investor', phone='+998907778899',
        )
        InvestorProfile.objects.create(
            user=i1, company_name="Olim Ventures", industries='it,education',
            budget_min=Decimal('50000000'), budget_max=Decimal('500000000'),
            bio='IT va ta\'lim sohalariga investitsiya qilaman.',
        )

        i2 = User.objects.create_user(
            username='investor_madina', email='madina@example.com', password='parol12345',
            first_name='Madina', last_name='Saidova', role='investor', phone='+998901234567',
        )
        InvestorProfile.objects.create(
            user=i2, company_name="Madina Capital", industries='medicine,agriculture',
            budget_min=Decimal('100000000'), budget_max=Decimal('1000000000'),
            bio="Tibbiyot va qishloq xo'jaligi loyihalariga qiziqaman.",
        )

        # ---- G'oyalar ----
        idea1 = Idea.objects.create(
            author=s1,
            title="Smart Tashkent — shahar transporti uchun mobil ilova",
            short_description="Toshkentdagi avtobus va metroni real vaqt rejimida kuzatish ilovasi.",
            description=(
                "Smart Tashkent ilovasi yo'lovchilarga avtobus va metro qatnov vaqtlarini real "
                "vaqtda ko'rish, eng tez yo'nalishni tanlash va to'lovni QR-kod orqali amalga "
                "oshirish imkonini beradi. MVP tayyor, 5 ming foydalanuvchi sinovdan o'tkazgan."
            ),
            needed_amount=Decimal('300000000'),
            equity_percent=Decimal('15.00'),
            industry='it', region='toshkent_sh', status='new',
        )

        idea2 = Idea.objects.create(
            author=s2,
            title="EduPlay — bolalar uchun o'yin orqali matematika",
            short_description="6-12 yoshli bolalar uchun gamifikatsiya qilingan matematika platformasi.",
            description=(
                "EduPlay — bu maktab o'quvchilari uchun matematikani o'yin shaklida o'rgatadigan "
                "platforma. Bola har bir darsni o'yin sifatida o'taydi, ota-onalar progressini "
                "kuzatadi. Hozirda 200 oilada sinovdan o'tdi, natijalar yaxshi."
            ),
            needed_amount=Decimal('150000000'),
            equity_percent=Decimal('20.00'),
            industry='education', region='toshkent_sh', status='new',
        )

        idea3 = Idea.objects.create(
            author=s1,
            title="AgroSensor — qishloq xo'jaligi uchun IoT sensorlar",
            short_description="Tuproq namligi va haroratini o'lchaydigan arzon IoT qurilmalari.",
            description=(
                "Fermerlar uchun arzon va aniq sensorlar tarmog'i. Har bir sensor tuproq holatini "
                "o'lchab, mobil ilovaga ma'lumot yuboradi. Bu suv sarfini 30% kamaytiradi."
            ),
            needed_amount=Decimal('500000000'),
            equity_percent=Decimal('25.00'),
            industry='agriculture', region='samarqand', status='new',
        )

        # ---- Takliflar ----
        # 1-taklif: i1 → idea1 (kutilmoqda)
        offer1 = Offer.objects.create(
            idea=idea1, investor=i1,
            amount=Decimal('300000000'), equity_percent=Decimal('15.00'),
            message="Loyihangiz qiziq! MVP demo ko'rmoqchiman. Biznes-rejani jo'nating, iltimos.",
            status='pending',
        )

        # 2-taklif: i2 → idea3 (qabul qilinadi → idea3 funded bo'ladi)
        offer2 = Offer.objects.create(
            idea=idea3, investor=i2,
            amount=Decimal('500000000'), equity_percent=Decimal('25.00'),
            message="Qishloq xo'jaligi mening sohamiz. Investitsiyaga tayyorman.",
            status='accepted',
        )
        idea3.status = 'funded'
        idea3.save()

        # ---- Saqlangan g'oyalar ----
        SavedIdea.objects.create(user=i1, idea=idea2)
        SavedIdea.objects.create(user=i2, idea=idea1)

        # ---- Xabarlar ----
        Message.objects.create(
            offer=offer1, sender=i1,
            content="Salom Aziz! Sizning loyihangiz juda qiziq. Demo havolangizni jo'natsangiz.",
            is_read=True,
        )
        Message.objects.create(
            offer=offer1, sender=s1,
            content="Salom Olim aka! Albatta. Mana demo: https://example.com/demo. Biznes-rejani ham yuborayapman.",
            is_read=False,
        )

        Message.objects.create(
            offer=offer2, sender=i2,
            content="Tabriklayman! Bitim shartlarini batafsil muhokama qilamiz.",
            is_read=True,
        )

        self.stdout.write(self.style.SUCCESS("\n✅ Test maʼlumotlari muvaffaqiyatli yaratildi!"))
        self.stdout.write(self.style.SUCCESS("\nKirish uchun foydalanuvchilar (parol — barchasi: parol12345):"))
        self.stdout.write("  Startapchilar:")
        self.stdout.write("    • startup_aziz / parol12345")
        self.stdout.write("    • startup_dilnoza / parol12345")
        self.stdout.write("  Investorlar:")
        self.stdout.write("    • investor_olim / parol12345")
        self.stdout.write("    • investor_madina / parol12345")
