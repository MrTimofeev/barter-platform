from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView, TemplateView
from .models import Ad, ExchangeProposal
from .forms import AdForm, ProposalCreateForm, ProposalStatusForm
from django.db.models import Q
from django.db import connection
from django.views import View


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

        # Начинаем с фильтрации по is_active
        queryset = super().get_queryset().filter(is_active=True)
        print(f"Активных объявлений: {queryset.count()}")

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

        print(f"Итоговое количество объявлений: {queryset.count()}")
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
    form_class = ProposalCreateForm
    template_name = 'ads/proposal_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.ad_receiver = get_object_or_404(Ad, pk=kwargs['receiver_pk'])
        self.ad_sender = get_object_or_404(Ad, pk=kwargs['sender_pk'])

        # Проверка 1: Предложение самому себе
        if self.ad_sender.user == self.ad_receiver.user:
            messages.warning(
                request, "Нельзя предлагать обмен на свой же товар")
            return redirect(self.ad_receiver.get_absolute_url())

        # Проверка 2: Дубликат предложения
        if ExchangeProposal.objects.filter(
            ad_sender=self.ad_sender,
            ad_receiver=self.ad_receiver
        ).exists():
            messages.error(
                request, "Вы уже отправляли предложение для этого обмена")
            return redirect(self.ad_receiver.get_absolute_url())

        if not self.ad_sender.is_active or not self.ad_receiver.is_active:
            messages.error(
                request, "Обмен невозможен: одно из объявлений неактивно")
            return redirect(self.ad_receiver.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.ad_sender = self.ad_sender
        form.instance.ad_receiver = self.ad_receiver
        form.instance.status = 'pending'
        messages.success(self.request, "Предложение успешно отправлено!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ad_detail', kwargs={'pk': self.ad_receiver.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad_sender'] = self.ad_sender
        context['ad_receiver'] = self.ad_receiver
        return context


class ExchangeProposalUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ExchangeProposal
    form_class = ProposalStatusForm
    template_name = 'ads/update_proposal.html'

    def test_func(self):
        proposal = self.get_object()
        return proposal.ad_receiver.user == self.request.user and proposal.status == 'pending'

    def post(self, request, *args, **kwargs):
        # Должно появиться в консоли сервера
        print("POST запрос получен! Данные:", request.POST)

        return super().post(request, *args, **kwargs)

    def accept(self, request, *args, **kwargs):
        """Обработка принятия предложения"""
        proposal = self.get_object()
        if proposal.status != 'pending':
            messages.error(request, "Предложение уже обработано")
            return redirect('my_proposals')
        proposal = self.get_object()
        proposal.status = 'accepted'
        proposal.save()

        proposal.ad_sender.is_active = False
        proposal.ad_receiver.is_active = False
        proposal.ad_sender.save()
        proposal.ad_receiver.save()

        messages.success(request, "Обмен подтверждён! Объявления скрыты.")
        return redirect('my_proposals')

    def reject(self, request, *args, **kwargs):
        """Обработка отклонения предложения"""
        proposal = self.get_object()
        proposal.status = 'rejected'
        proposal.save()

        messages.warning(request, "Предложение отклонено.")
        return redirect('my_proposals')

    def get_success_url(self):
        return reverse('my_proposals')


class MyProposalsView(LoginRequiredMixin, TemplateView):
    template_name = 'ads/my_proposals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Получаем активную вкладку
        tab = self.request.GET.get('tab', 'received')

        context['active_tab'] = tab
        context['received_proposals'] = ExchangeProposal.objects.filter(
            ad_receiver__user=user
        ).select_related('ad_sender', 'ad_receiver')

        context['sent_proposals'] = ExchangeProposal.objects.filter(
            ad_sender__user=user
        ).select_related('ad_receiver', 'ad_sender')

        return context


class ProposalAcceptView(LoginRequiredMixin, View):
    """Обработка принятия предложения обмена"""

    def post(self, request, pk):
        proposal = get_object_or_404(
            ExchangeProposal,
            pk=pk,
            ad_receiver__user=request.user,  # Только получатель может принять
            status='pending'  # Только ожидающие предложения
        )

        # Обновляем статус
        proposal.status = 'accepted'
        proposal.save()

        # Делаем объявления неактивными
        proposal.ad_sender.is_active = False
        proposal.ad_receiver.is_active = False
        proposal.ad_sender.save()
        proposal.ad_receiver.save()

        messages.success(
            request, "Вы приняли предложение обмена! Объявления скрыты.")
        return redirect('my_proposals')


class ProposalRejectView(LoginRequiredMixin, View):
    """Обработка отклонения предложения обмена"""

    def post(self, request, pk):
        proposal = get_object_or_404(
            ExchangeProposal,
            pk=pk,
            ad_receiver__user=request.user,  # Только получатель может отклонить
            status='pending'  # Только ожидающие предложения
        )

        # Обновляем статус
        proposal.status = 'rejected'
        proposal.save()

        messages.warning(request, "Вы отклонили предложение обмена.")
        return redirect('my_proposals')


class ExchangeProposalDetailView(LoginRequiredMixin, DetailView):
    model = ExchangeProposal
    template_name = 'ads/proposal_detail.html'
    context_object_name = 'proposal'

    def get_queryset(self):
        return ExchangeProposal.objects.filter(
            Q(ad_sender__user=self.request.user) |
            Q(ad_receiver__user=self.request.user)
        )
