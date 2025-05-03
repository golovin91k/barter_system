from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic

from .constans import (
    CATEGORY_CHOICES, CONDITION_CHOICES, STATUS_CHOICES)
from .forms import (
    AdForm, ExchangeProposalFormCreate, ExchangeProposalFormUpdate)
from .models import Ad, ExchangeProposal


class AdsListView(generic.ListView):
    """Список всех объявлений."""
    model = Ad
    template_name = 'ads/list_ads.html'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()

        category = self.request.GET.get('category')
        condition = self.request.GET.get('condition')
        search = self.request.GET.get('search')

        if category:
            queryset = queryset.filter(category=category)
        if condition:
            queryset = queryset.filter(condition=condition)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search))

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = CATEGORY_CHOICES
        context['condition_choices'] = CONDITION_CHOICES
        return context


class AdCreateView(LoginRequiredMixin, generic.CreateView):
    """Создание объявления."""
    model = Ad
    template_name = 'ads/form_ad.html'
    form_class = AdForm

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        else:
            return self.handle_no_permission()
        messages.success(self.request, 'Объявление успешно создано!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ads:detail_ad', kwargs={'ad_pk': self.object.pk})


class AdDetailView(generic.DetailView):
    """Просмотр объявления."""
    model = Ad
    template_name = 'ads/detail_ad.html'
    pk_url_kwarg = 'ad_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['request_user_ads'] = Ad.objects.filter(
                user=self.request.user)
        return context


class AdUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Изменение объявления."""
    model = Ad
    template_name = 'ads/form_ad.html'
    form_class = AdForm
    pk_url_kwarg = 'ad_pk'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404('Объект не найден')
        if obj.is_available is False:
            raise PermissionDenied('Этот объект нельзя редактировать')
        return obj

    def get_success_url(self):
        messages.success(self.request, 'Объявление успешно изменено.')
        obj = self.object
        return reverse_lazy('ads:detail_ad', kwargs={'ad_pk': obj.pk})


class AdDeleteView(LoginRequiredMixin, generic.DeleteView):
    """Удаление объявления."""
    model = Ad
    pk_url_kwarg = 'ad_pk'
    success_url = reverse_lazy('ads:list_ads')
    template_name = 'ads/ad_confirm_delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404('Объект не найден')
        if obj.is_available is False:
            raise PermissionDenied('Этот объект нельзя удалить.')
        return obj

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'Объявление успешно удалено.')
        return HttpResponseRedirect(self.success_url)


class UserAvailableAdsView(LoginRequiredMixin, generic.ListView):
    """Отображение доступных для пользователя объявлений для обмена."""
    model = Ad
    template_name = 'ads/user_available_ads.html'
    paginate_by = 8
    pk_url_kwarg = 'ad_receiver_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad_receiver_pk = self.kwargs['ad_receiver_pk']
        context['ad_receiver_pk'] = ad_receiver_pk
        return context

    def get_queryset(self):
        queryset = Ad.objects.filter(
            Q(user=self.request.user) & Q(is_available=True)).order_by(
                '-created_at')
        return queryset


class ExcCreateView(LoginRequiredMixin, generic.CreateView):
    """Создание обмена."""
    model = ExchangeProposal
    template_name = 'ads/create_exc.html'
    form_class = ExchangeProposalFormCreate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['ad_receiver_pk'] = self.kwargs['ad_receiver_pk']
        kwargs['ad_sender_pk'] = self.kwargs['ad_sender_pk']
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ad_receiver_pk = self.kwargs['ad_receiver_pk']
        ad_sender_pk = self.kwargs['ad_sender_pk']

        ad_receiver = get_object_or_404(Ad, pk=ad_receiver_pk)
        ad_sender = get_object_or_404(Ad, pk=ad_sender_pk)

        context['ad_receiver'] = ad_receiver
        context['ad_sender'] = ad_sender

        return context

    def form_valid(self, form):
        ad_receiver_pk = self.kwargs['ad_receiver_pk']
        ad_sender_pk = self.kwargs['ad_sender_pk']

        ad_receiver = get_object_or_404(Ad, pk=ad_receiver_pk)
        ad_sender = get_object_or_404(Ad, pk=ad_sender_pk)

        form.instance.ad_receiver = ad_receiver
        form.instance.ad_sender = ad_sender
        form.instance.status = 'pending'

        return super().form_valid(form)

    def get_success_url(self):
        obj = self.object
        return reverse_lazy('ads:update_exc', kwargs={'exc_pk': obj.pk})


class ExcsListView(generic.ListView):
    """Список всех обменов."""
    model = ExchangeProposal
    template_name = 'ads/list_excs.html'
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()

        ad_receiver = self.request.GET.get('ad_receiver')
        ad_sender = self.request.GET.get('ad_sender')
        status = self.request.GET.get('status')

        if ad_receiver:
            queryset = queryset.filter(
                ad_receiver__user__username__iexact=ad_receiver)

        if ad_sender:
            queryset = queryset.filter(
                ad_sender__user__username__iexact=ad_sender)

        if status:
            queryset = queryset.filter(status__iexact=status)

        queryset = queryset.select_related(
            'ad_receiver__user',
            'ad_sender__user'
        ).order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad_senders'] = ExchangeProposal.objects.values_list(
            'ad_sender__user__username', flat=True).distinct()

        context['ad_receivers'] = ExchangeProposal.objects.values_list(
            'ad_receiver__user__username', flat=True).distinct()
        context['status_choices'] = STATUS_CHOICES
        return context


class ExcUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Рассмотрение заявки на обмен."""
    model = ExchangeProposal
    form_class = ExchangeProposalFormUpdate
    template_name = 'ads/update_exc.html'
    pk_url_kwarg = 'exc_pk'
    success_url = reverse_lazy('ads:user_excs')

    def form_valid(self, form):
        exchange = self.get_object()

        if exchange.ad_receiver.user != self.request.user:
            raise PermissionDenied(
                'Вы не можете рассмотреть это предложение обмена')

        if exchange.status != 'pending':
            raise PermissionDenied(
                'Этот обмен уже рассмотрен')

        new_status = form.cleaned_data['status']

        response = super().form_valid(form)

        if new_status == 'accepted':
            if exchange.ad_sender:
                exchange.ad_sender.is_available = False
                exchange.ad_sender.save()

            if exchange.ad_receiver:
                exchange.ad_receiver.is_available = False
                exchange.ad_receiver.save()

        return response


class ExcDeleteView(LoginRequiredMixin, generic.DeleteView):
    """Удаление заявки на обмен."""
    model = ExchangeProposal
    pk_url_kwarg = 'exc_pk'
    template_name = 'ads/exc_confirm_delete.html'
    success_url = reverse_lazy('ads:user_excs')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.ad_sender.user != self.request.user:
            raise PermissionDenied(
                'Вы не можете удалить это предложение обмена')
        return obj

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'Запрос обмена успешно удален.')
        return HttpResponseRedirect(self.get_success_url())


class UserAdsView(LoginRequiredMixin, generic.ListView):
    """Список объявлений пользователя."""
    model = Ad
    template_name = 'ads/user_ads.html'
    paginate_by = 8

    def get_queryset(self):
        queryset = Ad.objects.filter(
            Q(user=self.request.user)).order_by('-created_at')
        return queryset


class UserExcsView(LoginRequiredMixin, generic.ListView):
    """Список обменов пользователя."""
    model = ExchangeProposal
    template_name = 'ads/user_excs.html'
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()

        ad_receiver = self.request.GET.get('ad_receiver')
        ad_sender = self.request.GET.get('ad_sender')
        status = self.request.GET.get('status')

        if ad_receiver:
            queryset = queryset.filter(
                ad_receiver__user__username__iexact=ad_receiver)

        if ad_sender:
            queryset = queryset.filter(
                ad_sender__user__username__iexact=ad_sender)

        if status:
            queryset = queryset.filter(status__iexact=status)

        queryset = queryset.select_related(
            'ad_receiver__user',
            'ad_sender__user'
        ).order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad_senders'] = ExchangeProposal.objects.values_list(
            'ad_sender__user__username', flat=True).distinct()

        context['ad_receivers'] = ExchangeProposal.objects.values_list(
            'ad_receiver__user__username', flat=True).distinct()
        context['status_choices'] = STATUS_CHOICES
        return context
