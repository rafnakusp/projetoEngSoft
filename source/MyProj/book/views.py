from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from datetime import datetime, timedelta
from django.utils import timezone
from book.models import Rota, Voo, Status, ProgressoVoo
from django.db import connection, transaction

from .forms import formularioFiltroVoo, formularioCadastroVoo, FormularioFiltroRelatorioVoosRealizados, FormularioFiltroRelatorioVoosAtrasados
from django.db.models import Q, F

TABELAS_PADRAO_JA_FORAM_CRIADAS = False
USUARIO_LOGADO = ""
CONTAGEM_DE_FALHAS_NO_LOGIN = 0
tz = timezone.get_fixed_timezone(timedelta(hours=-3))

@csrf_exempt
def telaLogin(request):
    global CONTAGEM_DE_FALHAS_NO_LOGIN
    
    if CONTAGEM_DE_FALHAS_NO_LOGIN >= 3:
        return render(request, "loginbloqueado.html")

    if request.method == "GET":
        global USUARIO_LOGADO
        return render(request, "login.html")

    elif request.method == "POST":
        if request.POST["username"] == "operadordevoos" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "operadordevoos"
        elif (request.POST["username"] == "funcionariocompanhia" or request.POST["username"] == "operadordetorre" or request.POST["username"] == "piloto") and request.POST["password"] == "senha":
            USUARIO_LOGADO = "usuariostatus"
        elif request.POST["username"] == "gerentedeoperacoes" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "gerentedeoperacoes"        
        elif request.POST["username"] == "paineldevoo" and request.POST["password"] == "senha":
            USUARIO_LOGADO = "paineldevoo"          
        
        else:
            CONTAGEM_DE_FALHAS_NO_LOGIN += 1
            if CONTAGEM_DE_FALHAS_NO_LOGIN >= 3:
                return render(request, "loginbloqueado.html")
            return render(request, "login.html")

        CONTAGEM_DE_FALHAS_NO_LOGIN = 0
        return redirect("/telainicial/")

def telainicial(request):
    global TABELAS_PADRAO_JA_FORAM_CRIADAS
    # reseta_id_voos() #- descomentar quando quiser resetar a contagem das primary keys
    if not TABELAS_PADRAO_JA_FORAM_CRIADAS:
        criarTabelasProducao()
        TABELAS_PADRAO_JA_FORAM_CRIADAS = True

    template = 'telainicial.html'
    context = {
        'username': USUARIO_LOGADO,
    }
    return render(request, template, context)

################################################################################
####                               CRUD de voos                             ####
################################################################################

def crud(request):
    fronteira = FronteiraCrud()

    if request.method == "GET":
        form = formularioFiltroVoo()
        return render(request, "crud.html", {'formulario_voos': form})
    elif request.method == "POST":
        form = formularioFiltroVoo(request.POST) 

        if request.POST["tipo"] == "cadastrar":
            if form.is_valid():
                template = 'crudcadastrovoo.html'
                context = {
                    "novo_voo": formularioCadastroVoo(request.POST)
                }
                return render(request, template, context)

        elif request.POST["tipo"] == "filtrar" and form.is_valid():
            voos = fronteira.apresentaVoosFiltrados(form)
            if voos == None:
                template = 'errodeconsulta.html'
                context = {
                    "rota_errada": {
                        'aeroporto': form.data['rota'],
                        'aeroporto_origem': 'origem' if 'chegada' else 'destino'
                    }
                }
                return render(request, template, context)

            template = 'crud.html'
            context = {
                "formulario_voos": form,
                "voo_list": voos # context é a lista de voos já convertida
            }
            return render(request, template, context)

def crudCreate(request):
    fronteira = FronteiraCrud()
    form = formularioCadastroVoo(request.POST)
    if request.method == "POST":
        if form.is_valid():
            voo_criado = fronteira.criarVoo(form)
            if voo_criado == "rota_errada":
                template = 'errodecadastro.html'
                context = {
                    "rota_errada": {
                        'aeroporto': form.data['rota'],
                        'aeroporto_origem': 'origem' if 'chegada' else 'destino'
                    }
                }
                return render(request, template, context)
            elif voo_criado == "horario no passado":
                template = 'errodecadastro.html'
                context = {
                    "horario_passado": form.data['horario_previsto'],
                    "chegada": "horário de chegada" if voo_criado == "horario chegada no passado" else "horário de partida"
                }
                return render(request, template, context)
            else:
                template = 'cadastrarvoosucesso.html'
                context = {
                    "novo_voo": voo_criado
                }
                return render(request, template, context)
               
def crudConfirmarDelecao(request, vooid):
    context = {'vooid': vooid}
    return render(request, "deletarvooconfirmacao.html", context)


def crudDelete(request, vooid):
    fronteiraCrud = FronteiraCrud()
    fronteiraCrud.removePorId(vooid)
    return render(request, "deletarvoosucesso.html")

def crudUpdate(request, vooid):
    fronteiraCrud = FronteiraCrud()
    voo = Voo.objects.select_related("rota_voo").get(voo_id=vooid)

    if request.method == "POST":
        form = formularioCadastroVoo(request.POST)
        if form.is_valid():
            voo = fronteiraCrud.atualizaVoo(vooid, form)
            if voo == "rota_errada":
                    template = 'errodecadastro.html'
                    context = {
                        "rota_errada": {
                            'aeroporto': form.data['rota'],
                            'aeroporto_origem': 'origem' if 'chegada' else 'destino'
                        }
                    }
                    return render(request, template, context)
            elif voo == "horario no passado":
                    template = 'errodecadastro.html'
                    context = {
                        "horario_passado": form.data['horario_previsto'],
                        "chegada": "horário de chegada" if voo == "horario chegada no passado" else "horário de partida"
                    }
                    return render(request, template, context)
    
    form = fronteiraCrud.geraTelaUpdate(voo)
    template = 'updatevoo.html'
    context = {
        "voo": voo,
        'formulario': form
    }
    return render(request, template, context)

class FronteiraCrud():
    def __init__(self):
        self.controladorCrud = ControladorCrud()
    def apresentaVoosFiltrados(self, formulario):
        return self.controladorCrud.readVoos(formulario)
    def removePorId(self, vooid):
        return self.controladorCrud.deleteVoosPorId(vooid)
    def atualizaVoo(self, vooid, form):
        return self.controladorCrud.updateVoo(vooid, form)
    def criarVoo(self, form):
        return self.controladorCrud.createVoo(form)
    def geraTelaUpdate(self, voo):
        dados_voo = {
            "companhia": voo.companhia_aerea,
            "horario_previsto": voo.horario_previsto,
            "rota": voo.rota_voo.outro_aeroporto,
            "chegada": voo.rota_voo.chegada
        }
        return formularioCadastroVoo(dados_voo)

class ControladorCrud():
    formatoData = "%Y-%m-%dT%H:%M"

    def createVoo(self, form):
        agora = datetime.now(tz)

        companhia = form.data['companhia']
        horario_previsto = datetime.strptime(form.data['horario_previsto'], self.formatoData).replace(tzinfo=tz)
        rota = form.data['rota']
        chegada = True if 'chegada' in form.data else False

        if horario_previsto < agora:
            return "horario no passado"

        try:
           rota = Rota.objects.get(outro_aeroporto=rota, chegada=chegada)
        except:
            return "rota_errada"
        voo = Voo.objects.create(companhia_aerea=companhia,horario_previsto=horario_previsto, rota_voo = rota)
        ProgressoVoo.objects.create(status_voo=None, voo = voo, horario_real=None)

        return Voo.objects.select_related('rota_voo').get(voo_id=voo.pk)

    def readVoos(self, form):

        companhia = form.data['companhia']
        inicio_periodo_pesquisa = form.data['intervalo_previsto_0']
        fim_periodo_pesquisa = form.data['intervalo_previsto_1']
        rota = form.data['rota']
        chegada = True if 'chegada' in form.data else False
        
        voosFiltrados = Voo.objects.all()
        if rota != "":
            try:
                rota = Rota.objects.get(outro_aeroporto=rota, chegada=chegada)
            except:
                return None
            voosFiltrados = voosFiltrados.filter(rota_voo=rota)
        if companhia != "":
            voosFiltrados = voosFiltrados.filter(companhia_aerea=companhia)
        if inicio_periodo_pesquisa != "" or fim_periodo_pesquisa != "":
            if inicio_periodo_pesquisa == "":
                fppp = datetime.strptime(fim_periodo_pesquisa, self.formatoData).replace(tzinfo=tz)
                voosFiltrados = voosFiltrados.filter(horario_previsto__lte=fppp)
            elif fim_periodo_pesquisa == "":
                ippp = datetime.strptime(inicio_periodo_pesquisa, self.formatoData).replace(tzinfo=tz)
                voosFiltrados = voosFiltrados.filter(horario_previsto__gte=ippp)
            else:
                fppp = datetime.strptime(fim_periodo_pesquisa, self.formatoData).replace(tzinfo=tz)
                ippp = datetime.strptime(inicio_periodo_pesquisa, self.formatoData).replace(tzinfo=tz)
                voosFiltrados = voosFiltrados.filter(horario_previsto__range=[ippp, fppp])

        # for voo in voosFiltrados:
        #     print(voo)

        return voosFiltrados

    def deleteVoosPorId(self, vooid):
        Voo.objects.all().filter(voo_id=vooid).delete()

    def updateVoo(self, vooid, form):
        agora = datetime.now(tz)

        companhia = form.data['companhia']
        horario_previsto = datetime.strptime(form.data['horario_previsto'], self.formatoData).replace(tzinfo=tz)
        rota = form.data['rota']
        chegada = True if 'chegada' in form.data else False

        voo_antigo = Voo.objects.get(voo_id=vooid)

        if horario_previsto < agora and voo_antigo.horario_previsto >= agora: #Tentou alterar para o passado
            return "horario no passado"

        try:
           rota = Rota.objects.get(outro_aeroporto=rota, chegada=chegada)
        except:
            return "rota_errada"
        Voo.objects.all().filter(voo_id=vooid).update(companhia_aerea=companhia, horario_previsto=horario_previsto, rota_voo=rota)
        return Voo.objects.get(voo_id=vooid)


################################################################################
####          Atualizar o status de voos/ Painel de Monitoração             ####
################################################################################

@csrf_exempt
def monitoramentodevoos(request):
    if request.method == "GET":
        if Voo.objects.all().count() > 0:
            template = 'monitoramentodevoos.html'
            painel = PainelDeMonitoracao()
            context = {
                "voo_list": painel.apresentaVoosNaoFinalizados() # context é a lista de voos já convertida
            }
            return render(request, template, context)
        else:
            template = 'erronenhumvoo.html'
            return render(request, template)

@csrf_exempt
def painelDeMonitoracao(request):
    if request.method == "GET":
        template = 'painelmonitoracao.html'
        painel = PainelDeMonitoracao()
        context = {
            "voo_list": painel.apresentaVoosNaoFinalizados() # context é a lista de voos já convertida
        }
        return render(request, template, context)
    

def monitoramentodevooseditar(request, vooid):
    painel = PainelDeMonitoracao()
    template = 'monitoramentodevooseditar.html' 

    if request.method == "POST" and 'status' in request.POST:
        painel.atualizaStatusDeVoo(vooid, request.POST['status'])

    context = {
            "voo": painel.apresentaVoo(vooid), # context é a lista de voos já convertida
            "status_possiveis": painel.statusPossiveis(vooid)
    }
    return render(request, template, context)

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
        voos = ProgressoVoo.objects.all()#.select_related('status_voo', 'voo').extra(select={'val': "select chegada from Rota r, ProgressoVoo pv, Voo v on r.rota_id=v.rota_voo_id and v.voo_id = pv.voo_id"})
        
        timeoutVooSemstatus = datetime.now(tz=tz) + timedelta(days=2)
        timeout1hora = datetime.now(tz=tz) - timedelta(hours=1)# Timeout se cancelado ou atrasado há mais de 1 hora

        return voos.filter(~Q(status_voo__status_nome__in=['Cancelado', 'Aterrissado']) | Q(horario_real__gt=timeout1hora, voo__rota_voo__chegada=True) | Q(voo__horario_previsto__gt=timeout1hora, voo__rota_voo__chegada=False))\
                   .exclude(status_voo__isnull=True, voo__horario_previsto__gte=timeoutVooSemstatus)

    def apresentaVoo(self, vooid):
        return ProgressoVoo.objects.select_related('status_voo', 'voo').extra(select={'val': "select chegada from Rota r, ProgressoVoo pv, Voo v on r.rota_id=v.rota_voo_id and v.voo_id = pv.voo_id"}).get(voo_id=vooid)

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
            if voo.voo.rota_voo.chegada:
                status_possiveis = [em_voo]
            else:
                status_possiveis = [embarque, cancelado]
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
        elif status == 'Em voo' and voo.voo.rota_voo.chegada:
            status_possiveis = [aterrissado]
        else:
            status_possiveis = []

        return status_possiveis

    def atualizaStatusDeVoo(self, vooid, novo_status_id):
        voo = ProgressoVoo.objects.select_related('status_voo').get(voo_id=vooid)
        status_antigo = voo.status_voo
        voo.status_voo = Status.objects.get(status_id=novo_status_id)
        if ((voo.status_voo.status_nome in ["Em voo", "Aterrissado"] and status_antigo != None)):
            voo.horario_real = datetime.now(tz=tz)
        voo.save()
        
################################################################################
####                            Geração de relatório                        ####
################################################################################

def geracaoderelatorios(request):
    return render(request, "geracaoderelatorios.html")

def geracaoDeRelatoriosVoosRealizados(request):
    controleGeracaoRelatorios = ControleGeracaoRelatorios()

    if request.method == "POST":
        form = FormularioFiltroRelatorioVoosRealizados(request.POST)
        print(form)
        print(form.is_valid())

        if form.is_valid():
            context = {
                "progressovoo_list": controleGeracaoRelatorios.filtrarVoosRealizados(form)
            }
            return render(request, "relatoriovoosrealizados.html", context)

    form = FormularioFiltroRelatorioVoosRealizados()
    return render(request, "geracaoderelatoriovoosrealizados.html", {'formulario': form})

def geracaoDeRelatoriosVoosAtrasados(request):
    controleGeracaoRelatorios = ControleGeracaoRelatorios()

    if request.method == "POST":
        form = FormularioFiltroRelatorioVoosAtrasados(request.POST)

        if form.is_valid():
            companhia = form.data['companhia']
            status = form.data['status']
            atraso = form.data['atraso']
    
            context = {
                "progressovoo_list": controleGeracaoRelatorios.filtrarVoosAtrasados(status, companhia, atraso),
                "label_atraso": atraso
            }
            return render(request, "relatoriovoosatrasados.html", context)

    form = FormularioFiltroRelatorioVoosAtrasados()
    return render(request, "geracaoderelatoriovoosatrasados.html", {'formulario': form})


class ControleGeracaoRelatorios():
    formatoData = "%Y-%m-%dT%H:%M"

    def filtrarVoos(self, form):
        companhia = form.data['companhia']
        inicio_periodo_pesquisa_real = form.data['intervalo_real_0']
        fim_periodo_pesquisa_real = form.data['intervalo_real_1']
        print(inicio_periodo_pesquisa_real)

        voosQuerySet = ProgressoVoo.objects.all()
        if companhia != "":
            voosQuerySet = voosQuerySet.filter(voo__companhia_aerea=companhia)
        if inicio_periodo_pesquisa_real != "" or fim_periodo_pesquisa_real != "":
            if inicio_periodo_pesquisa_real == "":
                fppp = datetime.strptime(fim_periodo_pesquisa_real, self.formatoData).replace(tzinfo=tz)
                voosQuerySet = voosQuerySet.filter(horario_real__lte=fppp)
            elif fim_periodo_pesquisa_real == "":
                ippp = datetime.strptime(inicio_periodo_pesquisa_real, self.formatoData).replace(tzinfo=tz)
                voosQuerySet = voosQuerySet.filter(horario_real__gte=ippp)
            else:
                fppp = datetime.strptime(fim_periodo_pesquisa_real, self.formatoData).replace(tzinfo=tz)
                ippp = datetime.strptime(inicio_periodo_pesquisa_real, "%Y-%m-%dT%H:%M").replace(tzinfo=tz)
                voosQuerySet = voosQuerySet.filter(horario_real__range=[ippp, fppp])

        return voosQuerySet
    
    def filtrarVoosAtrasados(self, status, companhia, atraso):
        agora = datetime.now(tz)
        print(agora)
        voosQuerySet = ProgressoVoo.objects.all()
        tempo_atraso = None
        if status != "":
            if status == '-':
                voosQuerySet = voosQuerySet.filter(status_voo__isnull=True)
            else:
                voosQuerySet = voosQuerySet.filter(status_voo__status_nome__exact=status)
        if companhia != "":
            voosQuerySet = voosQuerySet.filter(voo__companhia_aerea__exact=companhia)
        if atraso != '':
            if atraso == '1-10min':
                tempo_atraso = timedelta(minutes=10)
                min_tempo_atraso = timedelta(minutes=1)
                voosQuerySet = voosQuerySet.filter(Q(horario_real__isnull=True, voo__horario_previsto__range=[agora-tempo_atraso, agora-min_tempo_atraso]) | \
                    Q(horario_real__range=[F('voo__horario_previsto') + min_tempo_atraso, F('voo__horario_previsto') + tempo_atraso]))
            elif atraso == '10min-1h':
                tempo_atraso = timedelta(hours=1)
                min_tempo_atraso = timedelta(minutes=10)
                voosQuerySet = voosQuerySet.filter(Q(horario_real__isnull=True, voo__horario_previsto__range=[agora-tempo_atraso, agora-min_tempo_atraso]) | \
                    Q(horario_real__range=[F('voo__horario_previsto') + min_tempo_atraso, F('voo__horario_previsto') + tempo_atraso]))
            elif atraso == '1-3h':
                tempo_atraso = timedelta(hours=3)
                min_tempo_atraso = timedelta(hours=1)
                voosQuerySet = voosQuerySet.filter(Q(horario_real__isnull=True, voo__horario_previsto__range=[agora-tempo_atraso, agora-min_tempo_atraso]) | \
                    Q(horario_real__range=[F('voo__horario_previsto') + min_tempo_atraso, F('voo__horario_previsto') + tempo_atraso]))
            elif atraso == '>3h':
                min_tempo_atraso = timedelta(hours=3)
                voosQuerySet = voosQuerySet.filter(Q(horario_real__isnull=True, voo__horario_previsto__lt=agora-min_tempo_atraso) | \
                    Q(horario_real__gt=F('voo__horario_previsto') + min_tempo_atraso))

        return voosQuerySet.filter(Q(horario_real__gt=F('voo__horario_previsto')) | Q(horario_real__isnull=True, voo__horario_previsto__lt=agora))\
            .exclude(status_voo__status_nome="Cancelado").order_by('voo_id').distinct() # Voos cancelados nao estao atrasados

    def filtrarVoosRealizados(self, form):
        return self.filtrarVoos(form).filter(horario_real__isnull=False).order_by('voo_id').distinct()

################################################################################
####                         Criador de tabelas                             ####
################################################################################

def criarTabelasProducao():
    agora = datetime.now(tz=tz)

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
    Voo.objects.create(companhia_aerea='American Airlines',horario_previsto=datetime(2022, 8, 11, 12, 15, tzinfo=tz), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='American Airlines')
    status = Status.objects.get(status_nome='Em voo')
    ProgressoVoo.objects.create(status_voo = status, voo = voo,horario_real=None)

    Voo.objects.create(companhia_aerea='American Airlines',horario_previsto=datetime(2022, 8, 11, 12, 16, tzinfo=tz), rota_voo = rota_1)

    # voo cancelado a menos de 1 hora
    rota_2 = Rota.objects.get(outro_aeroporto='GRU')
    Voo.objects.create(companhia_aerea='Azul',horario_previsto=(agora - timedelta(minutes = 50)), rota_voo = rota_2)
    voo2 = Voo.objects.get(companhia_aerea='Azul')
    status2 = Status.objects.get(status_nome='Cancelado')
    ProgressoVoo.objects.create(status_voo = status2, voo = voo2, horario_real=None)

    # voo cancelado a mais de 1 hora
    Voo.objects.create(companhia_aerea='GOL',horario_previsto=(agora - timedelta(hours = 2)), rota_voo = rota_2)
    voo2 = Voo.objects.get(companhia_aerea='GOL')
    ProgressoVoo.objects.create(status_voo = status2, voo = voo2, horario_real=None)

    # voo Aterrissado a menos de 1 hora
    Voo.objects.create(companhia_aerea='LATAM',horario_previsto=(agora - timedelta(hours = 1)), rota_voo = rota_1)
    voo2 = Voo.objects.get(companhia_aerea='LATAM')
    status3 = Status.objects.get(status_nome='Aterrissado')
    ProgressoVoo.objects.create(status_voo = status3, voo = voo2, horario_real=(agora - timedelta(minutes = 50)))

    # voo Aterrissado a mais de 1 hora
    Voo.objects.create(companhia_aerea='TAM',horario_previsto=(agora - timedelta(minutes = 2)), rota_voo = rota_1)
    voo2 = Voo.objects.get(companhia_aerea='TAM')
    ProgressoVoo.objects.create(status_voo = status3, voo = voo2, horario_real=(agora - timedelta(minutes = 65)))

    # voo em Embarque (diferente de 'cancelado' ou 'Aterrissado')
    Voo.objects.create(companhia_aerea='American Air',horario_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='American Air')
    status4 = Status.objects.get(status_nome='Embarque')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_real=None)

    # voo programado (diferente de 'cancelado' ou 'Aterrissado')
    Voo.objects.create(companhia_aerea='Amer',horario_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='Amer')
    status4 = Status.objects.get(status_nome='Programado')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_real=None)

    # voo taxiando (diferente de 'cancelado' ou 'Aterrissado')
    Voo.objects.create(companhia_aerea='American',horario_previsto=(agora + timedelta(minutes = 3)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='American')
    status4 = Status.objects.get(status_nome='Taxiando')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_real=None)

    # voo pronto (diferente de 'cancelado' ou 'Aterrissado')
    Voo.objects.create(companhia_aerea='A',horario_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='A')
    status4 = Status.objects.get(status_nome='Pronto')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_real=None)

    # voo autorizado (diferente de 'cancelado' ou 'Aterrissado')
    Voo.objects.create(companhia_aerea='B',horario_previsto=(agora-timedelta(minutes = 3)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='B')
    status4 = Status.objects.get(status_nome='Autorizado')
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_real=None)

    # voo sem status que terminará a mais de 2 dias de agora
    Voo.objects.create(companhia_aerea='D',horario_previsto=(agora+timedelta(days = 2, hours=1)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='D')
    ProgressoVoo.objects.create(status_voo = None, voo = voo, horario_real=None)

    # voo sem status
    Voo.objects.create(companhia_aerea='C',horario_previsto=(agora-timedelta(minutes = 3)), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='C')
    ProgressoVoo.objects.create(status_voo = None, voo = voo, horario_real=None)

    # voo sem status
    Voo.objects.create(companhia_aerea='E',horario_previsto=(agora-timedelta(hours= 2)), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='E')
    ProgressoVoo.objects.create(status_voo = None, voo = voo, horario_real=None)

    # voo sem status
    Voo.objects.create(companhia_aerea='Qatar Airways',horario_previsto=(agora-timedelta(hours= 1)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='Qatar Airways')
    ProgressoVoo.objects.create(status_voo = None, voo = voo, horario_real=None)

def criarTabelasProducaoComRequest(request):
    # reseta_id_voos()
    criarTabelasProducao()
    return render(request, "telainicial.html")

def reseta_id_voos():
    cursor = connection.cursor()

    # Operação de modificação de dado - commit obrigatório
    cursor.execute("UPDATE SQLITE_SEQUENCE SET seq = 0;")
    transaction.commit()
