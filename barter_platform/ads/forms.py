from django import forms
from .models import Ad, ExchangeProposal


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Подробное описание товара'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название товара'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
        }

        labels = {
            'image_url': 'Ссылка на изображение',
            'category': 'Категория',
            'condition': 'Состояние'
        }

        def __init__(self, *args, **kwargs):
            self.request = kwargs.pop('request', None)
            super().__init__(*args, **kwargs)

        def clean(self):
            cleaned_data = super().clean()
            if not self.request or not self.request.user.is_authenticated:
                raise forms.ValidationError("Вы должны быть авторизованы")
            return cleaned_data


class ProposalCreateForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишите ваше предложение...'
            })
        }
        labels = {
            'comment': 'Ваше предложение'
        }


class ProposalStatusForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = []
