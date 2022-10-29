from asyncio.windows_events import NULL
from django.db import connection
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from datetime import datetime, timedelta, tzinfo
from django.utils import timezone
from book.models import Rota, Voo, Status, ProgressoVoo

USUARIO_LOGADO = ""
CONTAGEM_DE_FALHAS_NO_LOGIN = 0

@csrf_exempt
def bookview(request):
    global CONTAGEM_DE_FALHAS_NO_LOGIN
    print("==========================================")
    print(request.method)
    print(request.POST)
    
    if CONTAGEM_DE_FALHAS_NO_LOGIN >= 3:
        return render(request, "loginbloqueado.html")

    if request.method == "GET":
        global USUARIO_LOGADO
        return render(request, "login.html")

    elif request.method == "POST":
        if request.POST["username"] == "operadordevoos" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "operadordevoos"
        elif request.POST["username"] == "usuariostatus" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "usuariostatus"
        elif request.POST["username"] == "gerentedeoperacoes" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "gerentedeoperacoes"        
        
        else:
            CONTAGEM_DE_FALHAS_NO_LOGIN += 1
            if CONTAGEM_DE_FALHAS_NO_LOGIN >= 3:
                return render(request, "loginbloqueado.html")
            return render(request, "login.html")

        CONTAGEM_DE_FALHAS_NO_LOGIN = 0
        return redirect("/telainicial/")

def telainicial(request):
    template = loader.get_template('telainicial.html')
    context = {
        'username': USUARIO_LOGADO,
    }
    return HttpResponse(template.render(context, request))

def crud(request):
    return render(request, "crud.html")

def monitoramentodevoos(request):
    template = loader.get_template('monitoramentodevoos.html')
    painel = PainelDeMonitoracao()
    context = {
        "voo_list": painel.apresentavoosnaofinalizados() # context é a lista de voos já convertida
    }
    return HttpResponse(template.render(context, request))

def geracaoderelatorios(request):
    return render(request, "geracaoderelatorios.html")

################################################################################
####                               CRUD de voos                             ####
################################################################################

################################################################################
####          Atualizar o status de voos/ Painel de Monitoração             ####
################################################################################

class PainelDeMonitoracao():
    def __init__(self):
        self.controlador = ControladorAtualizarStatusDeVoo()

    def apresentaVoosNaoFinalizados(self):
        return self.controlador.apresentaVoosNaoFinalizados()

    def atualizarVoo():
        pass

class ControladorAtualizarStatusDeVoo():

    def apresentaVoosNaoFinalizados(self):
        voos = ProgressoVoo.objects.select_related('status_voo', 'voo').extra(select={'val': "select chegada from Rota r, ProgressoVoo pv, Voo v on r.rota_id=v.rota_voo_id and v.voo_id = pv.voo_id"})
        
        voosfiltrados = []
        for voo in voos:
            hcr = datetime(1, 1, 1, 0, 0, tzinfo=timezone.utc) if voo.horario_chegada_real==None else voo.horario_chegada_real
            if ((voo.status_voo.status_nome not in ['Cancelado', 'Aterrisado']) | (datetime.now(tz=timezone.utc) - timedelta(hours=1) < hcr) | (datetime.now(tz=timezone.utc) - timedelta(hours = 1) < voo.voo.horario_partida_previsto)):
               voosfiltrados.append(voo)
        
        voosformatados = []
        for voofiltrado in voosfiltrados:
            vooformatado = {
                "voo_id": voofiltrado.voo.voo_id,
                "companhia_aerea": voofiltrado.voo.companhia_aerea,
                "aeroporto_origem": voofiltrado.voo.rota_voo.outro_aeroporto if voofiltrado.voo.rota_voo.chegada else "Este aeroporto",
                "aeroporto_destino": "Este aeroporto" if voofiltrado.voo.rota_voo.chegada else voofiltrado.voo.rota_voo.outro_aeroporto,
                "status": voofiltrado.status_voo.status_nome,
                "horario_partida_previsto": voofiltrado.voo.horario_partida_previsto.strftime('%H:%M'),
                "horario_chegada_previsto": voofiltrado.voo.horario_chegada_previsto.strftime('%H:%M'),
                "horario_partida_real": "-" if voofiltrado.horario_partida_real == None else voofiltrado.horario_partida_real.strftime('%H:%M'),
                "horario_chegada_real": "-" if voofiltrado.horario_chegada_real == None else voofiltrado.horario_chegada_real.strftime('%H:%M')
            }
            voosformatados.append(vooformatado)

        return voosformatados

################################################################################
####                            Geração de relatório                        ####
################################################################################