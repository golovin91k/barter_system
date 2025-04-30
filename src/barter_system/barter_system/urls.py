from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import include, path, reverse_lazy


urlpatterns = [
    path('barter_system/', include('ads.urls')),
    path('barter_system/auth/', include('django.contrib.auth.urls')),
    path('barter_system/admin/', admin.site.urls),
    path(
        'barter_system/auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('ads:list'),
        ),
        name='registration',
    ),
]
