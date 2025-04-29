from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import Ad
from .forms import AdForm

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


def ad_list(request):
    ads = Ad.objects.all().order_by('-created_at')
    return render(request,  'ads/ad_list.html', {'ads': ads})
