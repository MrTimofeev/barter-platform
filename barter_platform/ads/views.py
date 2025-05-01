from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView, TemplateView
from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm
from django.db.models import Q
from django.db import connection


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ad_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')


class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'


class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):
        return reverse('ad_detail', kwargs={'pk': self.object.pk})


class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ad_list')

    def test_func(self):
        return self.get_object().user == self.request.user


class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    paginate_by = 10
    context_object_name = 'ads'

    def get_queryset(self):
        print("\n=== НАЧАЛО ФИЛЬТРАЦИИ ===")

        queryset = super().get_queryset()
        print(f"Всего объявлений до фильтрации: {queryset.count()}")

        # Получаем параметры
        search = self.request.GET.get('q')
        category = self.request.GET.get('category')
        condition = self.request.GET.get('condition')

        # Применяем фильтры
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
            print(f"Применён поиск: '{search}'")

        if category:
            queryset = queryset.filter(category=category)
            print(f"Применена категория: '{category}'")

        if condition:
            queryset = queryset.filter(condition=condition)
            print(f"Применено состояние: '{condition}'")

        print(f"Всего объявлений после фильтрации: {queryset.count()}")
        print("Последний SQL запрос:",
              connection.queries[-1]['sql'] if connection.queries else "Нет запросов")

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search_query': self.request.GET.get('q', ''),
            'selected_category': self.request.GET.get('category', ''),
            'selected_condition': self.request.GET.get('condition', ''),
            'categories': Ad.CATEGORY_CHOICE,
            'conditions': Ad.CONDITION_CHOICE,
        })
        return context


class ExchangeProposalCreateView(LoginRequiredMixin, CreateView):
    form_class = ExchangeProposalForm
    template_name = 'ads/proposal_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.ad_receiver = get_object_or_404(Ad, pk=kwargs['receiver_pk'])
        self.ad_sender = get_object_or_404(Ad, pk=kwargs['sender_pk'])
        
        # Проверка 1: Предложение самому себе
        if self.ad_sender.user == self.ad_receiver.user:
            messages.warning(request, "Нельзя предлагать обмен на свой же товар")
            return redirect(self.ad_receiver.get_absolute_url())
        
        # Проверка 2: Дубликат предложения
        if ExchangeProposal.objects.filter(
            ad_sender=self.ad_sender,
            ad_receiver=self.ad_receiver
        ).exists():
            messages.error(request, "Вы уже отправляли предложение для этого обмена")
            return redirect(self.ad_receiver.get_absolute_url())
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.ad_sender = self.ad_sender
        form.instance.ad_receiver = self.ad_receiver
        messages.success(self.request, "Предложение успешно отправлено!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ad_detail', kwargs={'pk': self.ad_receiver.pk})


class ExchangeProposalUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ExchangeProposal
    fields = ['status']
    template_name = 'ads/proposal_update.html'

    def test_func(self):
        return self.get_object().ad_receiver.user == self.request.user

    def form_valid(self, form):
        messages.success(
            self.request, f"Статус предложения изменен на: {form.instance.get_status_display()}")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('my_proposals')


class MyProposalsView(LoginRequiredMixin, TemplateView):
    template_name = 'ads/my_proposals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'sent_proposals': ExchangeProposal.objects.filter(
                ad_sender__user=self.request.user
            ).select_related('ad_receiver'),
            'received_proposals': ExchangeProposal.objects.filter(
                ad_receiver__user=self.request.user
            ).select_related('ad_sender'),
        })
        return context


class UpdateProposalView(LoginRequiredMixin, UpdateView):
    model = ExchangeProposal
    fields = ['status']
    template_name = 'ads/update_proposal.html'

    def test_func(self):
        return self.get_object().ad_receiver.user == self.request.user

    def get_initial(self):
        if 'status' in self.request.GET:
            return {'status': self.request.GET['status']}
        return super().get_initial()

    def get_success_url(self):
        return reverse('my_proposals')


def ad_list(request):
    ads = Ad.objects.all().order_by('-created_at')
    return render(request,  'ads/ad_list.html', {'ads': ads})
