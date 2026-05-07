"""G'oyalar, takliflar, saqlanganlar va xabarlar uchun viewlar."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import User
from .forms import IdeaForm, IdeaSearchForm, MessageForm, OfferForm
from .models import Idea, Message, Offer, SavedIdea


# ---------------------- HOME ----------------------

def home(request):
    """Asosiy sahifa: statistika, so'nggi g'oyalar, top g'oyalar, top investorlar."""
    total_ideas = Idea.objects.count()
    funded_ideas = Idea.objects.filter(status='funded').count()
    total_users = User.objects.count()
    total_startups = User.objects.filter(role='startup').count()
    total_investors = User.objects.filter(role='investor').count()
    funded_amount = Offer.objects.filter(status='accepted').aggregate(s=Sum('amount'))['s'] or 0

    latest_ideas = Idea.objects.filter(status='new').select_related('author')[:6]

    # Eng ko'p taklif olgan / moliyalashtirilgan g'oyalar
    top_ideas = (
        Idea.objects.annotate(off_count=Count('offers'))
        .order_by('-off_count', '-created_at')[:5]
    )

    top_investors = (
        User.objects.filter(role='investor')
        .annotate(off_count=Count('offers_made'))
        .filter(off_count__gt=0)
        .order_by('-off_count')[:5]
    )

    context = {
        'stats': {
            'total_ideas': total_ideas,
            'funded_ideas': funded_ideas,
            'total_users': total_users,
            'total_startups': total_startups,
            'total_investors': total_investors,
            'funded_amount': funded_amount,
        },
        'latest_ideas': latest_ideas,
        'top_ideas': top_ideas,
        'top_investors': top_investors,
    }
    return render(request, 'ideas/home.html', context)


# ---------------------- IDEAS ----------------------

def idea_list(request):
    """Barcha g'oyalar — qidiruv va filterlar bilan."""
    form = IdeaSearchForm(request.GET or None)
    qs = Idea.objects.select_related('author').all()

    # Investorlar faqat 'new' g'oyalarni ko'rishi shart
    if request.user.is_authenticated and request.user.is_investor:
        qs = qs.filter(status='new')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        industry = form.cleaned_data.get('industry')
        region = form.cleaned_data.get('region')
        status = form.cleaned_data.get('status')
        amount_min = form.cleaned_data.get('amount_min')
        amount_max = form.cleaned_data.get('amount_max')

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(short_description__icontains=q) | Q(description__icontains=q))
        if industry:
            qs = qs.filter(industry=industry)
        if region:
            qs = qs.filter(region=region)
        if status and not (request.user.is_authenticated and request.user.is_investor):
            qs = qs.filter(status=status)
        if amount_min is not None:
            qs = qs.filter(needed_amount__gte=amount_min)
        if amount_max is not None and amount_max > 0:
            qs = qs.filter(needed_amount__lte=amount_max)

    return render(request, 'ideas/idea_list.html', {
        'ideas': qs,
        'form': form,
    })


def idea_detail(request, pk):
    idea = get_object_or_404(Idea.objects.select_related('author'), pk=pk)

    # Investorlar faqat ochiq g'oyalarni ko'rishi shart, ammo o'z taklifini berganlarni ham ko'rsatamiz
    if request.user.is_authenticated and request.user.is_investor and idea.status != 'new':
        # Agar ushbu investor taklif bergan bo'lsa, ko'ra oladi
        has_offer = idea.offers.filter(investor=request.user).exists()
        if not has_offer:
            messages.warning(request, "Bu g'oya endi mavjud emas yoki yopilgan.")
            return redirect('ideas:list')

    user_offer = None
    if request.user.is_authenticated and request.user.is_investor:
        user_offer = idea.offers.filter(investor=request.user).first()

    is_saved = False
    if request.user.is_authenticated and request.user.is_investor:
        is_saved = SavedIdea.objects.filter(user=request.user, idea=idea).exists()

    offer_form = OfferForm()

    return render(request, 'ideas/idea_detail.html', {
        'idea': idea,
        'user_offer': user_offer,
        'is_saved': is_saved,
        'offer_form': offer_form,
    })


@login_required
def idea_create(request):
    if not request.user.is_startup:
        messages.error(request, "Faqat startapchilar g'oya joylashi mumkin.")
        return redirect('ideas:list')

    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.author = request.user
            idea.save()
            messages.success(request, "G'oya muvaffaqiyatli joylandi!")
            return redirect(idea.get_absolute_url())
    else:
        form = IdeaForm()
    return render(request, 'ideas/idea_form.html', {'form': form, 'is_create': True})


@login_required
def idea_edit(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if idea.author != request.user:
        return HttpResponseForbidden("Bu g'oyani tahrirlashga ruxsatingiz yo'q.")

    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES, instance=idea)
        if form.is_valid():
            form.save()
            messages.success(request, "G'oya yangilandi.")
            return redirect(idea.get_absolute_url())
    else:
        form = IdeaForm(instance=idea)
    return render(request, 'ideas/idea_form.html', {
        'form': form, 'is_create': False, 'idea': idea
    })


@login_required
@require_POST
def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if idea.author != request.user:
        return HttpResponseForbidden("Bu g'oyani o'chirishga ruxsatingiz yo'q.")
    idea.delete()
    messages.success(request, "G'oya o'chirildi.")
    return redirect('ideas:my_ideas')


@login_required
def my_ideas(request):
    if not request.user.is_startup:
        messages.error(request, "Bu sahifa faqat startapchilar uchun.")
        return redirect('ideas:home')

    ideas_qs = (
        request.user.ideas
        .annotate(off_count=Count('offers'))
        .order_by('-created_at')
    )
    return render(request, 'ideas/my_ideas.html', {'ideas': ideas_qs})


# ---------------------- OFFERS ----------------------

@login_required
@require_POST
def offer_create(request, idea_pk):
    if not request.user.is_investor:
        messages.error(request, "Faqat investorlar taklif yuborishi mumkin.")
        return redirect('ideas:detail', pk=idea_pk)

    idea = get_object_or_404(Idea, pk=idea_pk)

    if idea.status != 'new':
        messages.error(request, "Bu g'oya hozir takliflarga ochiq emas.")
        return redirect('ideas:detail', pk=idea_pk)

    if idea.author == request.user:
        messages.error(request, "O'zingizning g'oyangizga taklif yubora olmaysiz.")
        return redirect('ideas:detail', pk=idea_pk)

    if Offer.objects.filter(idea=idea, investor=request.user, status='pending').exists():
        messages.warning(request, "Siz bu g'oyaga allaqachon taklif yuborgansiz (kutilmoqda).")
        return redirect('ideas:detail', pk=idea_pk)

    form = OfferForm(request.POST)
    if form.is_valid():
        offer = form.save(commit=False)
        offer.idea = idea
        offer.investor = request.user
        offer.save()
        messages.success(request, "Taklif yuborildi! Startapchidan javob kuting.")
        return redirect('ideas:detail', pk=idea_pk)

    # Forma xato bo'lsa, idea_detail sahifasiga formani qaytaramiz
    user_offer = idea.offers.filter(investor=request.user).first()
    is_saved = SavedIdea.objects.filter(user=request.user, idea=idea).exists()
    return render(request, 'ideas/idea_detail.html', {
        'idea': idea,
        'user_offer': user_offer,
        'is_saved': is_saved,
        'offer_form': form,
    })


@login_required
def my_offers(request):
    if not request.user.is_investor:
        messages.error(request, "Bu sahifa faqat investorlar uchun.")
        return redirect('ideas:home')

    offers = request.user.offers_made.select_related('idea', 'idea__author').all()
    return render(request, 'ideas/my_offers.html', {'offers': offers})


@login_required
def received_offers(request):
    if not request.user.is_startup:
        messages.error(request, "Bu sahifa faqat startapchilar uchun.")
        return redirect('ideas:home')

    offers = (
        Offer.objects
        .filter(idea__author=request.user)
        .select_related('idea', 'investor')
        .order_by('-created_at')
    )
    return render(request, 'ideas/received_offers.html', {'offers': offers})


@login_required
@require_POST
def offer_accept(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    if offer.idea.author != request.user:
        return HttpResponseForbidden("Ruxsat yo'q.")

    if offer.status != 'pending':
        messages.warning(request, "Bu taklif allaqachon ko'rib chiqilgan.")
        return redirect('ideas:received_offers')

    # Qabul qilish
    offer.status = 'accepted'
    offer.save()

    # G'oyani 'funded' qilish, qolgan kutilayotgan takliflarni avtomatik rad etish
    idea = offer.idea
    idea.status = 'funded'
    idea.save()
    Offer.objects.filter(idea=idea, status='pending').exclude(pk=offer.pk).update(status='rejected')

    messages.success(request, "Taklif qabul qilindi! G'oya 'Moliyalashtirilgan' deb belgilandi.")
    return redirect('ideas:received_offers')


@login_required
@require_POST
def offer_reject(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    if offer.idea.author != request.user:
        return HttpResponseForbidden("Ruxsat yo'q.")

    if offer.status != 'pending':
        messages.warning(request, "Bu taklif allaqachon ko'rib chiqilgan.")
        return redirect('ideas:received_offers')

    offer.status = 'rejected'
    offer.save()
    messages.info(request, "Taklif rad etildi.")
    return redirect('ideas:received_offers')


# ---------------------- SAVED IDEAS ----------------------

@login_required
@require_POST
def toggle_save(request, idea_pk):
    if not request.user.is_investor:
        return JsonResponse({'error': 'Faqat investorlar uchun.'}, status=403)

    idea = get_object_or_404(Idea, pk=idea_pk)
    saved, created = SavedIdea.objects.get_or_create(user=request.user, idea=idea)
    if not created:
        saved.delete()
        messages.info(request, "G'oya saqlanganlardan olib tashlandi.")
        is_saved = False
    else:
        messages.success(request, "G'oya saqlandi.")
        is_saved = True

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'ideas:list'
    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect('ideas:detail', pk=idea_pk)


@login_required
def saved_ideas(request):
    if not request.user.is_investor:
        messages.error(request, "Bu sahifa faqat investorlar uchun.")
        return redirect('ideas:home')

    saved = (
        request.user.saved_ideas
        .select_related('idea', 'idea__author')
        .order_by('-created_at')
    )
    return render(request, 'ideas/saved_ideas.html', {'saved': saved})


# ---------------------- MESSAGES (CHAT) ----------------------

@login_required
def offer_chat(request, pk):
    offer = get_object_or_404(
        Offer.objects.select_related('idea', 'investor', 'idea__author'),
        pk=pk
    )

    # Faqat startapchi (g'oya muallifi) yoki investor (taklif beruvchi) ko'ra oladi
    if request.user != offer.investor and request.user != offer.idea.author:
        return HttpResponseForbidden("Ruxsat yo'q.")

    # Kelgan xabarlarni "ko'rilgan" qilamiz
    Message.objects.filter(offer=offer, is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.offer = offer
            msg.sender = request.user
            msg.save()
            return redirect('ideas:offer_chat', pk=pk)
    else:
        form = MessageForm()

    chat_messages = offer.messages.select_related('sender').all()

    # Suhbatdosh
    other_user = offer.idea.author if request.user == offer.investor else offer.investor

    return render(request, 'messaging/chat.html', {
        'offer': offer,
        'chat_messages': chat_messages,
        'form': form,
        'other_user': other_user,
    })


@login_required
def inbox(request):
    """Foydalanuvchining barcha chatlari (kim bilan suhbatlashgan)."""
    if request.user.is_startup:
        offers = (
            Offer.objects
            .filter(idea__author=request.user, messages__isnull=False)
            .distinct()
            .select_related('idea', 'investor')
        )
    else:
        offers = (
            Offer.objects
            .filter(investor=request.user, messages__isnull=False)
            .distinct()
            .select_related('idea', 'idea__author')
        )

    # Har bir taklif uchun oxirgi xabar va o'qilmaganlar soni
    items = []
    for offer in offers:
        last_msg = offer.messages.order_by('-created_at').first()
        unread = offer.messages.exclude(sender=request.user).filter(is_read=False).count()
        other = offer.idea.author if request.user == offer.investor else offer.investor
        items.append({
            'offer': offer,
            'last_message': last_msg,
            'unread': unread,
            'other_user': other,
        })

    return render(request, 'messaging/inbox.html', {'items': items})
