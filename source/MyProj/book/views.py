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
    painel = PainelDeMonitoracao()
    template = loader.get_template('monitoramentodevooseditar.html')  

    if request.method == "POST" and 'status' in request.POST:
        painel.atualizaStatusDeVoo(vooid, request.POST['status'])

    context = {
            "voo": painel.apresentaVoo(vooid), # context é a lista de voos já convertida
            "status_possiveis": painel.statusPossiveis(vooid)
    }
    return HttpResponse(template.render(context, request))

def geracaoderelatorios(request):
    return render(request, "geracaoderelatorios.html")

def crud(request):
    controladorCrud = ControladorCrud()

    if request.method == "GET":
        form = formularioCadastroVoo()
        return render(request, "crud.html", {'formulario': form})
    elif request.method == "POST":
        print(request.POST)

        form = formularioCadastroVoo(request.POST)

        companhia = form.data['companhia']
        horario_partida = form.data['horario_partida']
        horario_chegada = form.data['horario_chegada']
        rota = form.data['rota']
        chegada = True if 'chegada' in form.data else False

        if request.POST["tipo"] == "cadastrar":
            if form.is_valid():
                controladorCrud.createVoo(companhia=companhia, horario_partida=horario_partida, horario_chegada=horario_chegada, rota=rota)
                return render(request, "cadastrarvoosucesso.html")

        elif request.POST["tipo"] == "filtrar":
            template = loader.get_template('crudlistavoos.html')
            fronteira = FronteiraCrud()
            context = {
                "voo_list": fronteira.apresentaVoosFiltrados(companhia, horario_partida, horario_chegada, rota, chegada) # context é a lista de voos já convertida
            }
            return HttpResponse(template.render(context, request))


def crudDelete(request, vooid):
    fronteiraCrud = FronteiraCrud()
    fronteiraCrud.removePorId(vooid)
    return render(request, "deletarvoosucesso.html")

def criarTabelasProducao():
    agora = datetime.now(tz=timezone.utc)

    ProgressoVoo.objects.all().delete()
    Voo.objects.all().delete()
    Status.objects.all().delete()
    Rota.objects.all().delete()

    Status.objects.create(status_nome='Aterrissado')
    Status.objects.create(status_nome='Cancelado')
    Status.objects.create(status_nome='Embarque')
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

    rota_1 = Rota.objects.get(outro_aeroporto='Santos Dumont')
    Voo.objects.create(companhia_aerea='American Airlines',horario_partida_previsto=datetime(2022, 8, 11, 10, 30, tzinfo=timezone.utc),horario_chegada_previsto=datetime(2022, 8, 11, 12, 16, tzinfo=timezone.utc), rota_voo = rota_1)

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

    # voo Aterrissado a menos de 1 hora
    Voo.objects.create(companhia_aerea='LATAM',horario_partida_previsto=(agora - timedelta(hours = 2)),horario_chegada_previsto=(agora - timedelta(hours = 1)), rota_voo = rota_1)
    voo2 = Voo.objects.get(companhia_aerea='LATAM')
    status3 = Status.objects.get(status_nome='Aterrissado')
    ProgressoVoo.objects.create(status_voo = status3, voo = voo2, horario_partida_real=(agora - timedelta(minutes = 118)), horario_chegada_real=(agora - timedelta(minutes = 50)))

    # voo Aterrissado a mais de 1 hora
    Voo.objects.create(companhia_aerea='TAM',horario_partida_previsto=(agora - timedelta(hours = 3)),horario_chegada_previsto=(agora - timedelta(minutes = 2)), rota_voo = rota_1)
    voo2 = Voo.objects.get(companhia_aerea='TAM')
    ProgressoVoo.objects.create(status_voo = status3, voo = voo2, horario_partida_real=(agora - timedelta(minutes = 179)), horario_chegada_real=(agora - timedelta(minutes = 65)))

    # voo em Embarque (diferente de 'cancelado' ou 'Aterrissado')
    Voo.objects.create(companhia_aerea='American Air',horario_partida_previsto=(agora + timedelta(minutes = 20)),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='American Air')
    status4 = Status.objects.get(status_nome='Embarque')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_partida_real=None,horario_chegada_real=None)

    # voo programado (diferente de 'cancelado' ou 'Aterrissado')
    Voo.objects.create(companhia_aerea='Amer',horario_partida_previsto=(agora + timedelta(minutes = 15)),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='Amer')
    status4 = Status.objects.get(status_nome='Programado')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_partida_real=None,horario_chegada_real=None)

    # voo taxiando (diferente de 'cancelado' ou 'Aterrissado')
    Voo.objects.create(companhia_aerea='American',horario_partida_previsto=(agora + timedelta(minutes = 3)),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='American')
    status4 = Status.objects.get(status_nome='Taxiando')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_partida_real=None,horario_chegada_real=None)

    # voo pronto (diferente de 'cancelado' ou 'Aterrissado')
    Voo.objects.create(companhia_aerea='A',horario_partida_previsto=(agora),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='A')
    status4 = Status.objects.get(status_nome='Pronto')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_partida_real=None,horario_chegada_real=None)

    # voo autorizado (diferente de 'cancelado' ou 'Aterrissado')
    Voo.objects.create(companhia_aerea='B',horario_partida_previsto=(agora-timedelta(minutes = 3)),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='B')
    status4 = Status.objects.get(status_nome='Autorizado')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_partida_real=None,horario_chegada_real=None)

    # voo sem status
    Voo.objects.create(companhia_aerea='C',horario_partida_previsto=(agora-timedelta(minutes = 3)),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='C')
    ProgressoVoo.objects.create(status_voo = None, voo = voo, horario_partida_real=None,horario_chegada_real=None)

def criarTabelasProducaoComRequest(request):
    criarTabelasProducao()
    return render(request, "telainicial.html")

################################################################################
####                               CRUD de voos                             ####
################################################################################

class ControladorCrud():
    def createVoo(self, companhia, horario_partida, horario_chegada, rota):
        rota = Rota.objects.get(outro_aeroporto=rota)
        Voo.objects.create(companhia_aerea=companhia,horario_partida_previsto=horario_partida,horario_chegada_previsto=horario_chegada, rota_voo = rota)

    def readVoos(self, companhia, horario_partida, horario_chegada, rota, chegada):
        if companhia != "":
            rota = Rota.objects.get(outro_aeroporto=rota, chegada=chegada)
            return Voo.objects.all().filter(companhia_aerea=companhia, horario_partida_previsto=horario_partida,horario_chegada_previsto=horario_chegada, rota_voo=rota)
        else:
            return Voo.objects.all()

    def deleteVoosPorId(self, vooid):
        Voo.objects.all().filter(voo_id=vooid).delete()

class FronteiraCrud():
    controladorCrud = ControladorCrud()
    def apresentaVoosFiltrados(self, companhia, horario_partida, horario_chegada, rota, chegada):
        return self.controladorCrud.readVoos(companhia, horario_partida, horario_chegada, rota, chegada)
    def removePorId(self, vooid):
        return self.controladorCrud.deleteVoosPorId(vooid)

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

    def statusPossiveis(self, vooid):
        return self.controlador.statusPossiveis(vooid)

    def atualizaStatusDeVoo(self, vooid, statusid):
        self.controlador.atualizaStatusDeVoo(vooid, statusid)

class ControladorAtualizarStatusDeVoo():

    def apresentaVoosNaoFinalizados(self):
        voos = ProgressoVoo.objects.select_related('status_voo', 'voo').extra(select={'val': "select chegada from Rota r, ProgressoVoo pv, Voo v on r.rota_id=v.rota_voo_id and v.voo_id = pv.voo_id"})
        
        voosfiltrados = []
        for voo in voos:
            hcr = datetime(1, 1, 1, 0, 0, tzinfo=timezone.utc) if voo.horario_chegada_real==None else voo.horario_chegada_real
            if voo.status_voo == None:
                voosfiltrados.append(voo)
            elif ((voo.status_voo.status_nome not in ['Cancelado', 'Aterrissado']) | (datetime.now(tz=timezone.utc) - timedelta(hours=1) < hcr) | (datetime.now(tz=timezone.utc) - timedelta(hours = 1) < voo.voo.horario_partida_previsto)):
               voosfiltrados.append(voo)
        
        voosformatados = []
        for voofiltrado in voosfiltrados:
            vooformatado = {
                "voo_id": voofiltrado.voo.voo_id,
                "companhia_aerea": voofiltrado.voo.companhia_aerea,
                "aeroporto_origem": voofiltrado.voo.rota_voo.outro_aeroporto if voofiltrado.voo.rota_voo.chegada else "Este aeroporto",
                "aeroporto_destino": "Este aeroporto" if voofiltrado.voo.rota_voo.chegada else voofiltrado.voo.rota_voo.outro_aeroporto,
                "status": "-" if voofiltrado.status_voo == None else voofiltrado.status_voo.status_nome,
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
                "status": "-" if voo.status_voo == None else voo.status_voo.status_nome,
                "horario_partida_previsto": voo.voo.horario_partida_previsto.strftime('%H:%M'),
                "horario_chegada_previsto": voo.voo.horario_chegada_previsto.strftime('%H:%M'),
                "horario_partida_real": "-" if voo.horario_partida_real == None else voo.horario_partida_real.strftime('%H:%M'),
                "horario_chegada_real": "-" if voo.horario_chegada_real == None else voo.horario_chegada_real.strftime('%H:%M')
            }
        
        return vooformatado

    def statusPossiveis(self, vooid):
        voo = ProgressoVoo.objects.select_related('status_voo').get(voo_id=vooid)
        todos_status = Status.objects.all()
        embarque = todos_status.get(status_nome='Embarque')
        cancelado = todos_status.get(status_nome='Cancelado')
        em_voo = todos_status.get(status_nome='Em voo')
        programado = todos_status.get(status_nome='Programado')
        taxiando = todos_status.get(status_nome='Taxiando')
        pronto = todos_status.get(status_nome='Pronto')
        autorizado = todos_status.get(status_nome='Autorizado')
        aterrissado = todos_status.get(status_nome='Aterrissado')

        status = None if voo.status_voo == None else voo.status_voo.status_nome
        if status == None:
            status_possiveis = [embarque, cancelado, em_voo]
        elif status == 'Embarque':
            status_possiveis = [programado, cancelado]
        elif status == 'Programado':
            status_possiveis = [taxiando, cancelado]
        elif status == 'Taxiando':
            status_possiveis = [pronto, cancelado]
        elif status == 'Pronto':
            status_possiveis = [autorizado, cancelado]
        elif status == 'Autorizado':
            status_possiveis = [em_voo]
        elif status == 'Em voo':
            status_possiveis = [aterrissado]
        else:
            status_possiveis = []

        return status_possiveis

    def atualizaStatusDeVoo(self, vooid, novo_status_id):
        print(novo_status_id)
        voo = ProgressoVoo.objects.select_related('status_voo').get(voo_id=vooid)
        voo.status_voo = Status.objects.get(status_id=novo_status_id)
        if voo.status_voo.status_nome == "Autorizado":
            voo.horario_partida_real = datetime.now(tz=timezone.utc)
        elif voo.status_voo.status_nome == "Aterrissado":
            voo.horario_chegada_real = datetime.now(tz=timezone.utc)
        voo.save()

################################################################################
####                            Geração de relatório                        ####
################################################################################
