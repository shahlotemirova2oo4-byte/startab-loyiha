# 🚀 StartUp.uz — Yoshlar uchun Startap Platforma

Django asosida yaratilgan to'liq funksional veb-platforma. Yosh tadbirkorlar
g'oyalarini joylashi, investorlar esa ularga taklif yuborishi, suhbat qurishi
va loyihalarni moliyalashtirishi mumkin.

## ✨ Asosiy imkoniyatlar

- **Ikki rolli foydalanuvchilar:** Startapchi va Investor
- **G'oyalarni joylash:** sarlavha, tavsif, mablag', ulush, soha, hudud, fayl (rasm/PDF)
- **Investitsiya takliflari:** Investor → Startapchi (qabul/rad etish)
- **Qidiruv va filterlar:** soha, hudud, mablag' oralig'i, status
- **Saqlangan g'oyalar:** investor sevimlilarini saqlaydi
- **Ichki xabar almashish:** har bir taklifga biriktirilgan chat
- **Statistika va reyting:** top g'oyalar va faol investorlar
- **Admin panel:** barcha modellarni boshqarish uchun
- **Mobil va desktopga moslashgan dizayn** (Bootstrap 5)

## 📋 Talablar

- Python **3.10+**
- pip
- (ixtiyoriy) virtualenv

## 🛠 Ishga tushirish

### 1. Loyihani arxivdan chiqaring va papkaga kiring

```bash
cd startup_platform
```

### 2. Virtual muhit yarating va aktivlashtiring

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Bog'liqliklarni o'rnating

```bash
pip install -r requirements.txt
```

### 4. Maʼlumotlar bazasini tayyorlang

```bash
python manage.py makemigrations accounts ideas
python manage.py migrate
```

### 5. Admin (superuser) yarating

```bash
python manage.py createsuperuser
```

### 6. Test maʼlumotlarini yuklang (ixtiyoriy, lekin tavsiya etiladi)

```bash
python manage.py seed_data
```

Bu komanda quyidagilarni yaratadi:
- 2 ta startapchi: `startup_aziz`, `startup_dilnoza`
- 2 ta investor: `investor_olim`, `investor_madina`
- 3 ta g'oya
- 2 ta taklif (1 tasi qabul qilingan)
- Saqlangan g'oyalar va xabarlar

**Barcha test akkountlar uchun parol:** `parol12345`

### 7. Serverni ishga tushiring

```bash
python manage.py runserver
```

Brauzerda oching: <http://127.0.0.1:8000/>

Admin panel: <http://127.0.0.1:8000/admin/>

## 🎮 Sinash bo'yicha qadamlar

1. **Bosh sahifa** — statistika, top g'oyalar va so'nggi g'oyalarni ko'ring.
2. **Investor sifatida kirish** (`investor_olim` / `parol12345`):
   - "G'oyalar" sahifasiga o'ting → bir g'oyani tanlang.
   - "Investitsiya qilish" formasiga taklif yozing.
   - "Saqlash" tugmasi orqali g'oyani sevimlilarga qo'shing.
   - "Mening takliflarim" sahifasidan yuborilganlarni ko'ring.
   - "Saqlanganlar"ni ko'ring.
3. **Startapchi sifatida kirish** (`startup_aziz` / `parol12345`):
   - "Mening g'oyalarim" → yangi g'oya joylang yoki tahrirlang.
   - "Kelgan takliflar" → taklifni qabul qiling yoki rad eting.
   - Qabul qilinganda g'oya statusi avtomatik **"Moliyalashtirilgan"** bo'ladi.
4. **Xabar almashish:**
   - Taklif yuborilgan/qabul qilinganidan keyin "Xabarlar" → suhbat oching.
   - Investor va startapchi o'rtasida xabarlar almashinadi.
5. **Filtrlar:**
   - G'oyalar sahifasida sohaga, hududga, mablag' oralig'iga ko'ra filterlang.

## 📂 Loyiha tuzilishi

```
startup_platform/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3                 ← migratsiyadan keyin yaratiladi
├── config/                    ← Django sozlamalari
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                  ← Foydalanuvchi va profillar
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── ideas/                     ← G'oyalar, takliflar, chat, saqlanganlar
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── context_processors.py
│   ├── templatetags/
│   └── management/commands/
│       └── seed_data.py
├── templates/                 ← HTML templatlar
│   ├── base.html
│   ├── partials/
│   ├── registration/
│   ├── accounts/
│   ├── ideas/
│   └── messaging/
├── static/css/main.css        ← Custom CSS
└── media/                     ← Foydalanuvchi yuklagan fayllar
```

## 🗄 Asosiy modellar

- **User** (custom): username, email, role (`startup`/`investor`), phone
- **StartupProfile** / **InvestorProfile**: rolga qarab qo'shimcha ma'lumotlar
- **Idea**: sarlavha, tavsif, mablag', ulush, soha, hudud, fayl, status
- **Offer**: taklif (mablag', ulush, status: pending/accepted/rejected)
- **SavedIdea**: investor saqlagan g'oyalar
- **Message**: taklifga biriktirilgan chat xabarlari (is_read holati bilan)

## 🔐 Xavfsizlik

- CSRF himoyasi barcha POST formalarida
- `@login_required` himoyalangan sahifalarda
- Ownership tekshiruvi (faqat o'z g'oyangizni tahrirlay/o'chira olasiz)
- Rolga asoslangan ruxsatlar (faqat investor taklif yuboradi, faqat startapchi qabul qiladi)
- Fayllar uchun cheklov: 10 MB, faqat rasm yoki PDF

## 🎨 Frontend

- **Bootstrap 5** (CDN orqali)
- **Bootstrap Icons** (CDN)
- Mobil va desktopga moslashgan responsive dizayn
- Custom CSS: `static/css/main.css`

## ⚙ Ishlab chiqish

Yangi g'oya yoki funksiya qo'shmoqchi bo'lsangiz:

```bash
# Modellarni o'zgartirgandan keyin
python manage.py makemigrations
python manage.py migrate

# Statik fayllarni yig'ish (production uchun)
python manage.py collectstatic
```

## 📝 Litsenziya

Demo loyiha. Erkin foydalanish uchun.
