"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from django.shortcuts import render, redirect
from django.conf import settings
from django.conf.urls.static import static

from apps.pessoas.views import login_view

def inicio_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'inicio.html')


urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticação
    path('', login_view, name='login'),
    path('sair/', LogoutView.as_view(next_page='login'), name='logout'),

    # Aplicação
    path('inicio/', inicio_view, name='inicio'),
    path('pessoas/', include('apps.pessoas.urls')),
    path('pets/', include('apps.pets.urls')),
    path('resgates/', include('apps.resgates.urls')),
    path('atendimentos/', include('apps.atendimentos.urls')),
    path('estoque/', include('apps.estoque.urls')),
    path('fornecedores/', include('apps.fornecedores.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )