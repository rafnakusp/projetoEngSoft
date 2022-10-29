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
from django.db.models import Q
from .forms import formularioCadastroVoo

USUARIO_LOGADO = ""
CONTAGEM_DE_FALHAS_NO_LOGIN = 0

@csrf_exempt
def bookview(request):
    global CONTAGEM_DE_FALHAS_NO_LOGIN
    print("====================Debug======================")
    print(f"{request.method=}")
    print(f"{request.body=}")
    print(f"{request.POST=}")
    
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
    criarTabelasProducao()
    template = loader.get_template('telainicial.html')
    context = {
        'username': USUARIO_LOGADO,
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
def monitoramentodevoos(request):
    if request.method == "GET":
        template = loader.get_template('monitoramentodevoos.html')
        painel = PainelDeMonitoracao()
        context = {
            "voo_list": painel.apresentaVoosNaoFinalizados() # context é a lista de voos já convertida
        }
        return HttpResponse(template.render(context, request))
    

def monitoramentodevooseditar(request, vooid):
    if request.method == "GET":
        template = loader.get_template('monitoramentodevooseditar.html')
        painel = PainelDeMonitoracao()
        context = {
            "voo": painel.apresentaVoo(vooid) # context é a lista de voos já convertida
        }
        return HttpResponse(template.render(context, request))
    elif request.method == "POST":
        print(f"{request.POST['id']}")
        return render(request, "monitoramentodevooseditar.html")

def geracaoderelatorios(request):
    return render(request, "geracaoderelatorios.html")

def crud(request):
    controladorCrud = ControladorCrud()

    if request.method == "GET":
        form = formularioCadastroVoo()
        return render(request, "crud.html", {'formulario': form})
    elif request.method == "POST":
        form = formularioCadastroVoo(request.POST)
        if form.is_valid():
            companhia = form.data['companhia']
            partida = form.data['horario_partida']
            chegada = form.data['horario_chegada']
            rota = form.data['rota']

            controladorCrud.createVoo(companhia=companhia, partida=partida, chegada=chegada, rota_str=rota)
            return render(request, "cadastrarvoosucesso.html")

def criarTabelasProducao():
    agora = datetime.now(tz=timezone.utc)

    ProgressoVoo.objects.all().delete()
    Voo.objects.all().delete()
    Status.objects.all().delete()
    Rota.objects.all().delete()

    Status.objects.create(status_nome='Aterrisado')
    Status.objects.create(status_nome='Cancelado')
    Status.objects.create(status_nome='Embarcando')
    Status.objects.create(status_nome='Programado')
    Status.objects.create(status_nome='Taxiando')
    Status.objects.create(status_nome='Pronto')
    Status.objects.create(status_nome='Autorizado')
    Status.objects.create(status_nome='Em voo')


    Rota.objects.create(outro_aeroporto='Santos Dumont',chegada=True)
    Rota.objects.create(outro_aeroporto='GRU',chegada=False)
    Rota.objects.create(outro_aeroporto='Brasília',chegada=False)

    rota_1 = Rota.objects.get(outro_aeroporto='Santos Dumont')
    Voo.objects.create(companhia_aerea='American Airlines',horario_partida_previsto=datetime(2022, 8, 11, 10, 30, tzinfo=timezone.utc),horario_chegada_previsto=datetime(2022, 8, 11, 12, 15, tzinfo=timezone.utc), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='American Airlines')
    status = Status.objects.get(status_nome='Em voo')
    ProgressoVoo.objects.create(status_voo = status, voo = voo, horario_partida_real=datetime(2022, 8, 11, 10, 42, tzinfo=timezone.utc),horario_chegada_real=None)

    # voo cancelado a menos de 1 hora
    rota_2 = Rota.objects.get(outro_aeroporto='GRU')
    Voo.objects.create(companhia_aerea='Azul',horario_partida_previsto=(agora - timedelta(minutes = 50)),horario_chegada_previsto=(agora + timedelta(hours = 2)), rota_voo = rota_2)
    voo2 = Voo.objects.get(companhia_aerea='Azul')
    status2 = Status.objects.get(status_nome='Cancelado')
    ProgressoVoo.objects.create(status_voo = status2, voo = voo2, horario_partida_real=None, horario_chegada_real=None)

    # voo cancelado a mais de 1 hora
    Voo.objects.create(companhia_aerea='GOL',horario_partida_previsto=(agora - timedelta(hours = 2)),horario_chegada_previsto=(agora + timedelta(hours = 1)), rota_voo = rota_2)
    voo2 = Voo.objects.get(companhia_aerea='GOL')
    ProgressoVoo.objects.create(status_voo = status2, voo = voo2, horario_partida_real=None, horario_chegada_real=None)

    # voo aterrisado a menos de 1 hora
    Voo.objects.create(companhia_aerea='LATAM',horario_partida_previsto=(agora - timedelta(hours = 2)),horario_chegada_previsto=(agora - timedelta(hours = 1)), rota_voo = rota_1)
    voo2 = Voo.objects.get(companhia_aerea='LATAM')
    status3 = Status.objects.get(status_nome='Aterrisado')
    ProgressoVoo.objects.create(status_voo = status3, voo = voo2, horario_partida_real=(agora - timedelta(minutes = 118)), horario_chegada_real=(agora - timedelta(minutes = 50)))

    # voo aterrisado a mais de 1 hora
    Voo.objects.create(companhia_aerea='TAM',horario_partida_previsto=(agora - timedelta(hours = 3)),horario_chegada_previsto=(agora - timedelta(minutes = 2)), rota_voo = rota_1)
    voo2 = Voo.objects.get(companhia_aerea='TAM')
    ProgressoVoo.objects.create(status_voo = status3, voo = voo2, horario_partida_real=(agora - timedelta(minutes = 179)), horario_chegada_real=(agora - timedelta(minutes = 65)))

    # voo em embarque (diferente de 'cancelado' ou 'aterrisado')
    Voo.objects.create(companhia_aerea='American Air',horario_partida_previsto=(agora + timedelta(minutes = 20)),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='American Air')
    status4 = Status.objects.get(status_nome='Embarcando')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_partida_real=None,horario_chegada_real=None)

    # voo programado (diferente de 'cancelado' ou 'aterrisado')
    Voo.objects.create(companhia_aerea='Amer',horario_partida_previsto=(agora + timedelta(minutes = 15)),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='Amer')
    status4 = Status.objects.get(status_nome='Programado')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_partida_real=None,horario_chegada_real=None)

    # voo taxiando (diferente de 'cancelado' ou 'aterrisado')
    Voo.objects.create(companhia_aerea='American',horario_partida_previsto=(agora + timedelta(minutes = 3)),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='American')
    status4 = Status.objects.get(status_nome='Taxiando')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_partida_real=None,horario_chegada_real=None)

    # voo pronto (diferente de 'cancelado' ou 'aterrisado')
    Voo.objects.create(companhia_aerea='A',horario_partida_previsto=(agora),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='A')
    status4 = Status.objects.get(status_nome='Pronto')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_partida_real=None,horario_chegada_real=None)

    # voo autorizado (diferente de 'cancelado' ou 'aterrisado')
    Voo.objects.create(companhia_aerea='B',horario_partida_previsto=(agora-timedelta(minutes = 3)),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='B')
    status4 = Status.objects.get(status_nome='Autorizado')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_partida_real=None,horario_chegada_real=None)

def criarTabelasProducaoComRequest(request):
    criarTabelasProducao()
    return render(request, "telainicial.html")

################################################################################
####                               CRUD de voos                             ####
################################################################################

class ControladorCrud():
    def createVoo(self, companhia, partida, chegada, rota_str):
        rota = Rota.objects.get(outro_aeroporto=rota_str)
        Voo.objects.create(companhia_aerea=companhia,horario_partida_previsto=partida,horario_chegada_previsto=chegada, rota_voo = rota)

################################################################################
####          Atualizar o status de voos/ Painel de Monitoração             ####
################################################################################

class PainelDeMonitoracao():
    def __init__(self):
        self.controlador = ControladorAtualizarStatusDeVoo()

    def apresentaVoosNaoFinalizados(self):
        return self.controlador.apresentaVoosNaoFinalizados()

    def apresentaVoo(self, vooid):
        return self.controlador.apresentaVoo(vooid)

    def atualizaStatusDeVoo(self, vooid):
        return self.controlador.atualizaStatusDeVoo(vooid)

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

    def apresentaVoo(self, vooid):
        voo = ProgressoVoo.objects.select_related('status_voo', 'voo').extra(select={'val': "select chegada from Rota r, ProgressoVoo pv, Voo v on r.rota_id=v.rota_voo_id and v.voo_id = pv.voo_id"}).get(voo_id=vooid)

        vooformatado = {
                "voo_id": voo.voo.voo_id,
                "companhia_aerea": voo.voo.companhia_aerea,
                "aeroporto_origem": voo.voo.rota_voo.outro_aeroporto if voo.voo.rota_voo.chegada else "Este aeroporto",
                "aeroporto_destino": "Este aeroporto" if voo.voo.rota_voo.chegada else voo.voo.rota_voo.outro_aeroporto,
                "status": voo.status_voo.status_nome,
                "horario_partida_previsto": voo.voo.horario_partida_previsto.strftime('%H:%M'),
                "horario_chegada_previsto": voo.voo.horario_chegada_previsto.strftime('%H:%M'),
                "horario_partida_real": "-" if voo.horario_partida_real == None else voo.horario_partida_real.strftime('%H:%M'),
                "horario_chegada_real": "-" if voo.horario_chegada_real == None else voo.horario_chegada_real.strftime('%H:%M')
            }
        
        return vooformatado

    def atualizaStatusDeVoo(self, vooid):
        return vooid

################################################################################
####                            Geração de relatório                        ####
################################################################################
