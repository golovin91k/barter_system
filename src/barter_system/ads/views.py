from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.views.generic import TemplateView

from .forms import (
    AdForm, ExchangeProposalFormCreate, ExchangeProposalFormUpdate)
from .models import Ad, ExchangeProposal
from .constans import (
    CATEGORY_CHOICES, CONDITION_CHOICES, STATUS_CHOICES)


class AdsListView(generic.ListView):
    """Список всех заметок объявлений."""
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
    model = Ad
    template_name = 'ads/form_ad.html'
    form_class = AdForm
    pk_url_kwarg = 'ad_pk'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise PermissionDenied('Вы не можете редактировать это объявление')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        obj = self.object
        return reverse_lazy('ads:detail_ad', kwargs={'ad_pk': obj.pk})


class AdDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Ad
    pk_url_kwarg = 'ad_pk'
    success_url = reverse_lazy('ads:list')

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.success_url)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.user != request.user:
            raise PermissionDenied('Вы не можете удалить это объявление')

        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class UserAvailableAdsView(LoginRequiredMixin, generic.ListView):
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
            Q(user=self.request.user) & Q(is_available=True))
        return queryset


class ExcCreateView(LoginRequiredMixin, generic.CreateView):
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


class ExcUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = ExchangeProposal
    form_class = ExchangeProposalFormUpdate
    template_name = 'ads/update_exc.html'
    pk_url_kwarg = 'exc_pk'
    success_url = reverse_lazy('ads:user_excs')

    def form_valid(self, form):
        response = super().form_valid(form)

        exchange = self.object
        if exchange.status == 'accepted':
            if exchange.ad_sender:
                exchange.ad_sender.is_available = False
                exchange.ad_sender.save()

            if exchange.ad_receiver:
                exchange.ad_receiver.is_available = False
                exchange.ad_receiver.save()

        elif exchange.status == 'rejected':
            if exchange.ad_sender:
                exchange.ad_sender.is_available = True
                exchange.ad_sender.save()

            if exchange.ad_receiver:
                exchange.ad_receiver.is_available = True
                exchange.ad_receiver.save()

        elif exchange.status == 'pending':
            if exchange.ad_sender:
                exchange.ad_sender.is_available = True
                exchange.ad_sender.save()

            if exchange.ad_receiver:
                exchange.ad_receiver.is_available = True
                exchange.ad_receiver.save()
        return response


class ExcDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = ExchangeProposal
    pk_url_kwarg = 'exc_pk'
    success_url = reverse_lazy('ads:user_excs')

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.success_url)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.ad_sender.user != request.user:
            raise PermissionDenied(
                'Вы не можете удалить это предложение обмена')

        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class UserAdsView(LoginRequiredMixin, generic.ListView):
    model = Ad
    template_name = 'ads/user_ads.html'
    paginate_by = 8

    def get_queryset(self):
        queryset = Ad.objects.filter(Q(user=self.request.user))
        return queryset


class UserExcsView(LoginRequiredMixin, generic.ListView):
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


class Error(TemplateView):
    template_name = 'ads/error_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_message = self.request.session.get(
            'error_message', 'Произошла ошибка.')
        context['error_message'] = error_message
        if 'error_message' in self.request.session:
            del self.request.session['error_message']
        return context
