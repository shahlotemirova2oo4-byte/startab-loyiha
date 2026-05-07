"""G'oya, taklif va xabar formalari."""
from django import forms

from .models import Idea, Offer, Message


BS_INPUT = 'form-control'
BS_SELECT = 'form-select'


def _bootstrap_widgets(form):
    for name, field in form.fields.items():
        widget = field.widget
        if isinstance(widget, forms.Select):
            widget.attrs['class'] = BS_SELECT
        elif isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
            widget.attrs['class'] = 'form-check-input'
        else:
            widget.attrs['class'] = BS_INPUT


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = (
            'title', 'short_description', 'description',
            'needed_amount', 'equity_percent',
            'industry', 'region', 'file',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_widgets(self)

    def clean_equity_percent(self):
        value = self.cleaned_data['equity_percent']
        if value < 0 or value > 100:
            raise forms.ValidationError('Ulush 0 dan 100 gacha bo\'lishi kerak.')
        return value

    def clean_needed_amount(self):
        value = self.cleaned_data['needed_amount']
        if value <= 0:
            raise forms.ValidationError("Mablag' 0 dan katta bo'lishi kerak.")
        return value

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if f:
            name = f.name.lower()
            allowed = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf')
            if not name.endswith(allowed):
                raise forms.ValidationError('Faqat rasm (JPG, PNG, GIF, WEBP) yoki PDF.')
            if f.size > 10 * 1024 * 1024:
                raise forms.ValidationError('Fayl hajmi 10 MB dan oshmasligi kerak.')
        return f


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ('amount', 'equity_percent', 'message')
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ixtiyoriy xabar...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap_widgets(self)

    def clean_equity_percent(self):
        value = self.cleaned_data['equity_percent']
        if value < 0 or value > 100:
            raise forms.ValidationError("Ulush 0 dan 100 gacha bo'lishi kerak.")
        return value

    def clean_amount(self):
        value = self.cleaned_data['amount']
        if value <= 0:
            raise forms.ValidationError("Mablag' 0 dan katta bo'lishi kerak.")
        return value


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 2, 'class': BS_INPUT, 'placeholder': 'Xabaringizni yozing...'
            }),
        }


class IdeaSearchForm(forms.Form):
    """Asosiy ro'yxat sahifasi uchun qidirish/filtrlash formasi."""
    q = forms.CharField(
        label='Qidirish', required=False,
        widget=forms.TextInput(attrs={'class': BS_INPUT, 'placeholder': 'Sarlavha yoki tavsif...'}),
    )
    industry = forms.ChoiceField(
        label='Soha', required=False,
        choices=[('', '— Barchasi —')] + list(Idea.INDUSTRY_CHOICES),
        widget=forms.Select(attrs={'class': BS_SELECT}),
    )
    region = forms.ChoiceField(
        label='Hudud', required=False,
        choices=[('', '— Barchasi —')] + list(__import__('ideas.models', fromlist=['REGION_CHOICES']).REGION_CHOICES),
        widget=forms.Select(attrs={'class': BS_SELECT}),
    )
    status = forms.ChoiceField(
        label='Status', required=False,
        choices=[('', '— Barchasi —')] + list(Idea.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': BS_SELECT}),
    )
    amount_min = forms.DecimalField(
        label="Min mablag'", required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': BS_INPUT, 'placeholder': '0'}),
    )
    amount_max = forms.DecimalField(
        label="Max mablag'", required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': BS_INPUT, 'placeholder': '∞'}),
    )
