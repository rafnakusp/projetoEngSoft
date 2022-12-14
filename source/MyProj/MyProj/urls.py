"""MyProj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from book import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.telaLogin),
    path('telainicial/', views.telainicial),
    path('crud/', views.crud, name="crud"),
    path('monitoramentodevoos/', views.monitoramentodevoos),
    path('monitoramentodevooseditar/<int:vooid>/', views.monitoramentodevooseditar),
    path('geracaoderelatorios/voosrealizados/', views.geracaoDeRelatoriosVoosRealizados),
    path('geracaoderelatorios/voosatrasados/', views.geracaoDeRelatoriosVoosAtrasados),
    path('geracaoderelatorios/', views.geracaoderelatorios),
    path('criartabelasproducao/', views.criarTabelasProducaoComRequest),
    path('crud/delete/confirmar/<int:vooid>/', views.crudConfirmarDelecao),
    path('crud/delete/<int:vooid>/', views.crudDelete),
    path('crud/update/<int:vooid>/', views.crudUpdate),
    path('crud/create/', views.crudCreate),
    path('paineldemonitoracao/', views.painelDeMonitoracao)
]
