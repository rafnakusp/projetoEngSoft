from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import loader
from datetime import datetime, timedelta
from django.utils import timezone
from book.models import Rota, Voo, Status, ProgressoVoo
from django.db import connection, transaction

from .forms import formularioFiltroVoo, formularioCadastroVoo
from django.db.models import Q, F


from .forms import formularioCadastroVoo, FormularioFiltroRelatorio

USUARIO_LOGADO = ""
CONTAGEM_DE_FALHAS_NO_LOGIN = 0

@csrf_exempt
def telaLogin(request):
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
    reseta_id_voos() #- descomentar quando quiser resetar a contagem das primary keys
    criarTabelasProducao()
    template = loader.get_template('telainicial.html')
    context = {
        'username': USUARIO_LOGADO,
    }
    return HttpResponse(template.render(context, request))

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
                template = loader.get_template('crudcadastrovoo.html')
                context = {
                    "novo_voo": formularioCadastroVoo(request.POST)
                }
                return HttpResponse(template.render(context, request))

        elif request.POST["tipo"] == "filtrar":
            voos = fronteira.apresentaVoosFiltrados(form)
            if voos == None:
                template = loader.get_template('errodeconsulta.html')
                context = {
                    "rota_errada": {
                        'aeroporto': form.data['rota'],
                        'aeroporto_origem': 'origem' if 'chegada' else 'destino'
                    }
                }
                return HttpResponse(template.render(context, request))

            template = loader.get_template('crud.html')
            context = {
                "formulario_voos": form,
                "voo_list": voos # context é a lista de voos já convertida
            }
            return HttpResponse(template.render(context, request))

def crudCreate(request):
    print(request.POST)
    fronteira = FronteiraCrud()
    form = formularioCadastroVoo(request.POST)
    if request.method == "POST":
        if form.is_valid():
            voo_criado = fronteira.criarVoo(form)
            if voo_criado == "rota_errada":
                template = loader.get_template('errodecadastro.html')
                context = {
                    "rota_errada": {
                        'aeroporto': form.data['rota'],
                        'aeroporto_origem': 'origem' if 'chegada' else 'destino'
                    }
                }
                return HttpResponse(template.render(context, request))
            elif voo_criado == "chegada antes da partida":
                template = loader.get_template('errodecadastro.html')
                context = {
                    "chegada_antes": {
                        'horario_chegada': form.data['horario_chegada'],
                        'horario_partida': form.data['horario_partida']
                    }
                }
                return HttpResponse(template.render(context, request))
            elif voo_criado in ["horario chegada no passado", "horario partida no passado"]:
                template = loader.get_template('errodecadastro.html')
                context = {
                    "horario_passado": form.data['horario_chegada'] if voo_criado == "horario chegada no passado" else form.data['horario_partida'],
                    "chegada": "horário de chegada" if voo_criado == "horario chegada no passado" else "horário de partida"
                }
                return HttpResponse(template.render(context, request))
            elif voo_criado == "voo muito longo":
                template = loader.get_template('errodecadastro.html')
                context = {
                    "voo_longo": {
                        'horario_chegada': form.data['horario_chegada'],
                        'horario_partida': form.data['horario_partida']
                    }
                }
                return HttpResponse(template.render(context, request))
            else:
                template = loader.get_template('cadastrarvoosucesso.html')
                context = {
                    "novo_voo": voo_criado
                }
                return HttpResponse(template.render(context, request))
               


def crudDelete(request, vooid):
    fronteiraCrud = FronteiraCrud()
    fronteiraCrud.removePorId(vooid)
    return render(request, "deletarvoosucesso.html")

def crudUpdate(request, vooid):
    fronteiraCrud = FronteiraCrud()
    voo = Voo.objects.select_related("rota_voo").get(voo_id=vooid)

    if request.method == "POST":
        form = formularioCadastroVoo(request.POST)
        voo = fronteiraCrud.atualizaVoo(vooid, form)
        print(voo)
        if voo == "rota_errada":
                template = loader.get_template('errodecadastro.html')
                context = {
                    "rota_errada": {
                        'aeroporto': form.data['rota'],
                        'aeroporto_origem': 'origem' if 'chegada' else 'destino'
                    }
                }
                return HttpResponse(template.render(context, request))
        elif voo == "chegada antes da partida":
                template = loader.get_template('errodecadastro.html')
                context = {
                    "chegada_antes": {
                        'horario_chegada': form.data['horario_chegada'],
                        'horario_partida': form.data['horario_partida']
                    }
                }
                return HttpResponse(template.render(context, request))
        elif voo in ["horario chegada no passado", "horario partida no passado"]:
                template = loader.get_template('errodecadastro.html')
                context = {
                    "horario_passado": form.data['horario_chegada'] if voo == "horario chegada no passado" else form.data['horario_partida'],
                    "chegada": "horário de chegada" if voo == "horario chegada no passado" else "horário de partida"
                }
                return HttpResponse(template.render(context, request))
        elif voo == "voo muito longo":
                template = loader.get_template('errodecadastro.html')
                context = {
                    "voo_longo": {
                        'horario_chegada': form.data['horario_chegada'],
                        'horario_partida': form.data['horario_partida']
                    }
                }
                return HttpResponse(template.render(context, request))
    
    form = fronteiraCrud.geraTelaUpdate(voo)
    template = loader.get_template('updatevoo.html')
    context = {
        "voo": voo,
        'formulario': form
    }
    return HttpResponse(template.render(context, request))

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
            "horario_partida": voo.horario_partida_previsto,
            "horario_chegada": voo.horario_chegada_previsto,
            "rota": voo.rota_voo.outro_aeroporto,
            "chegada": voo.rota_voo.chegada
        }
        return formularioCadastroVoo(dados_voo)

class ControladorCrud():
    formatoData = "%Y-%m-%dT%H:%M"

    def createVoo(self, form):
        agora = datetime.now(timezone.utc)

        companhia = form.data['companhia']
        horario_partida = datetime.strptime(form.data['horario_partida'], self.formatoData).replace(tzinfo=timezone.utc)
        horario_chegada = datetime.strptime(form.data['horario_chegada'], self.formatoData).replace(tzinfo=timezone.utc)
        rota = form.data['rota']
        chegada = True if 'chegada' in form.data else False

        if horario_chegada < horario_partida:
            return "chegada antes da partida"
        elif horario_chegada < agora:
            return "horario chegada no passado"
        elif horario_partida < agora:
            return "horario partida no passado"
        elif horario_chegada - timedelta(hours=20) > horario_partida:
            return "voo muito longo" #https://valor.globo.com/empresas/noticia/2022/06/02/voo-mais-longo-do-mundo-contara-com-suites-de-luxo-e-area-para-alongamento-veja-fotos.ghtml

        try:
           rota = Rota.objects.get(outro_aeroporto=rota, chegada=chegada)
        except:
            return "rota_errada"
        voo = Voo.objects.create(companhia_aerea=companhia,horario_partida_previsto=horario_partida,horario_chegada_previsto=horario_chegada, rota_voo = rota)
        ProgressoVoo.objects.create(status_voo=None, voo = voo, horario_partida_real=None, horario_chegada_real=None)

        return Voo.objects.select_related('rota_voo').get(voo_id=voo.pk)

    def readVoos(self, form):
        earliest_date = datetime(1, 1, 1, 0, 0, tzinfo=timezone.utc)
        latest_date = datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)

        companhia = form.data['companhia']
        inicio_periodo_pesquisa_partida = form.data['intervalo_partida_0']
        fim_periodo_pesquisa_partida = form.data['intervalo_partida_1']
        inicio_periodo_pesquisa_chegada = form.data['intervalo_chegada_0']
        fim_periodo_pesquisa_chegada = form.data['intervalo_chegada_1']
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
        if inicio_periodo_pesquisa_partida != "" or fim_periodo_pesquisa_partida != "":
            if inicio_periodo_pesquisa_partida == "":
                fppp = datetime.strptime(fim_periodo_pesquisa_partida, self.formatoData).replace(tzinfo=timezone.utc)
                voosFiltrados = voosFiltrados.filter(horario_partida_previsto__range=[earliest_date, fppp])
            elif fim_periodo_pesquisa_partida == "":
                ippp = datetime.strptime(inicio_periodo_pesquisa_partida, self.formatoData).replace(tzinfo=timezone.utc)
                voosFiltrados = voosFiltrados.filter(horario_partida_previsto__range=[ippp, latest_date])
            else:
                fppp = datetime.strptime(fim_periodo_pesquisa_partida, self.formatoData).replace(tzinfo=timezone.utc)
                ippp = datetime.strptime(inicio_periodo_pesquisa_partida, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
                voosFiltrados = voosFiltrados.filter(horario_partida_previsto__range=[ippp, fppp])
        if inicio_periodo_pesquisa_chegada != "" or fim_periodo_pesquisa_chegada != "":
            if inicio_periodo_pesquisa_chegada == "":
                fppc = datetime.strptime(fim_periodo_pesquisa_chegada, self.formatoData).replace(tzinfo=timezone.utc)
                voosFiltrados = voosFiltrados.filter(horario_chegada_previsto__range=[earliest_date, fppc])
            elif fim_periodo_pesquisa_chegada == "":
                ippc = datetime.strptime(inicio_periodo_pesquisa_chegada, self.formatoData).replace(tzinfo=timezone.utc)
                voosFiltrados = voosFiltrados.filter(horario_chegada_previsto__range=[ippc, latest_date])
            else:
                fppc = datetime.strptime(fim_periodo_pesquisa_chegada, self.formatoData).replace(tzinfo=timezone.utc)
                ippc = datetime.strptime(inicio_periodo_pesquisa_chegada, self.formatoData).replace(tzinfo=timezone.utc)
                voosFiltrados = voosFiltrados.filter(horario_chegada_previsto__range=[ippc, fppc])

        # for voo in voosFiltrados:
        #     print(voo)

        return voosFiltrados

    def deleteVoosPorId(self, vooid):
        Voo.objects.all().filter(voo_id=vooid).delete()

    def updateVoo(self, vooid, form):
        agora = datetime.now(timezone.utc)

        companhia = form.data['companhia']
        horario_partida = datetime.strptime(form.data['horario_partida'], self.formatoData).replace(tzinfo=timezone.utc)
        horario_chegada = datetime.strptime(form.data['horario_chegada'], self.formatoData).replace(tzinfo=timezone.utc)
        rota = form.data['rota']
        chegada = True if 'chegada' in form.data else False

        voo_antigo = Voo.objects.get(voo_id=vooid)

        if horario_chegada < horario_partida:
            return "chegada antes da partida"
        elif horario_chegada < agora and voo_antigo.horario_chegada_previsto >= agora: #Tentou alterar para o passado
            return "horario chegada no passado"
        elif horario_partida < agora and voo_antigo.horario_partida_previsto >= agora: #Tentou alterar para o passado
            return "horario partida no passado"
        elif horario_chegada - timedelta(hours=20) > horario_partida:
            return "voo muito longo" #https://valor.globo.com/empresas/noticia/2022/06/02/voo-mais-longo-do-mundo-contara-com-suites-de-luxo-e-area-para-alongamento-veja-fotos.ghtml

        try:
           rota = Rota.objects.get(outro_aeroporto=rota, chegada=chegada)
        except:
            return "rota_errada"
        Voo.objects.all().filter(voo_id=vooid).update(companhia_aerea=companhia, horario_partida_previsto=horario_partida,horario_chegada_previsto=horario_chegada, rota_voo=rota)
        return Voo.objects.get(voo_id=vooid)


################################################################################
####          Atualizar o status de voos/ Painel de Monitoração             ####
################################################################################

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
                if datetime.now(tz=timezone.utc) + timedelta(days=2) > voo.voo.horario_chegada_previsto:
                   voosfiltrados.append(voo)
            elif ((voo.status_voo.status_nome not in ['Cancelado', 'Aterrissado']) | (datetime.now(tz=timezone.utc) - timedelta(hours=1) < hcr) | (datetime.now(tz=timezone.utc) - timedelta(hours = 1) < voo.voo.horario_partida_previsto)):
               voosfiltrados.append(voo)

        return voosfiltrados

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
        voo = ProgressoVoo.objects.select_related('status_voo').get(voo_id=vooid)
        status_antigo = voo.status_voo
        voo.status_voo = Status.objects.get(status_id=novo_status_id)
        if ((voo.status_voo.status_nome == "Autorizado") | ((status_antigo == None) & (voo.status_voo.status_nome == "Em voo"))):
            voo.horario_partida_real = datetime.now(tz=timezone.utc)
        elif voo.status_voo.status_nome == "Aterrissado":
            voo.horario_chegada_real = datetime.now(tz=timezone.utc)
        voo.save()
        
################################################################################
####                            Geração de relatório                        ####
################################################################################

def geracaoderelatorios(request):
    return render(request, "geracaoderelatorios.html")

def geracaoDeRelatoriosVoosRealizados(request):
    controleGeracaoRelatorios = ControleGeracaoRelatorios()

    if request.method == "POST":
        form = FormularioFiltroRelatorio(request.POST)

        companhia = form.data['companhia']
        timestamp_min = form.data['timestamp_min']
        timestamp_max = form.data['timestamp_max']

        context = {
            "progressovoo_list": controleGeracaoRelatorios.filtrarVoosRealizados(timestamp_min, timestamp_max)
        }
        return render(request, "relatoriovoosrealizados.html", context)

    form = FormularioFiltroRelatorio()
    return render(request, "geracaoderelatoriovoosrealizados.html", {'formulario': form})

def geracaoDeRelatoriosVoosAtrasados(request):
    controleGeracaoRelatorios = ControleGeracaoRelatorios()

    if request.method == "POST":
        form = FormularioFiltroRelatorio(request.POST)

        companhia = form.data['companhia']
        timestamp_min = form.data['timestamp_min']
        timestamp_max = form.data['timestamp_max']

        context = {
            "progressovoo_list": controleGeracaoRelatorios.filtrarVoosAtrasados(timestamp_min, timestamp_max, companhia)
        }
        return render(request, "relatoriovoosatrasados.html", context)

    form = FormularioFiltroRelatorio()
    return render(request, "geracaoderelatoriovoosatrasados.html", {'formulario': form})


class ControleGeracaoRelatorios():
    def filtrarVoos(self, timestamp_min, timestamp_max, companhia):
        voosQuerySet = ProgressoVoo.objects.select_related("voo", "status_voo")
        str(voosQuerySet.query)
        if companhia != "":
            voosQuerySet = voosQuerySet.filter(voo__companhia_aerea__exact=companhia)
        if timestamp_min != "":
            voosQuerySet = voosQuerySet.filter(horario_chegada_real__gt=timestamp_min)
        if timestamp_max != "":
            voosQuerySet = voosQuerySet.filter(horario_chegada_real__lt=timestamp_max)
        return voosQuerySet
    
    def filtrarVoosAtrasados(self, timestamp_min, timestamp_max, companhia):
        agora = datetime.now(timezone.utc)
        print(agora)
        return self.filtrarVoos(timestamp_min, timestamp_max, companhia).filter(Q(horario_chegada_real__gt=F('voo__horario_chegada_previsto')) | Q(horario_chegada_real__isnull=True, \
            horario_partida_real__gt=F('voo__horario_partida_previsto')) | Q(horario_partida_real__isnull=True, voo__horario_partida_previsto__lt=agora) | \
            Q(horario_chegada_real__isnull=True, voo__horario_chegada_previsto__lt=agora)).order_by('voo_id').distinct()

    def filtrarVoosRealizados(self, timestamp_min, timestamp_max):
        return self.filtrarVoos(timestamp_min, timestamp_max).filter(horario_chegada_real__isnull=False).order_by('voo_id').distinct()

################################################################################
####                         Criador de tabelas                             ####
################################################################################

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
    ProgressoVoo.objects.create(status_voo = status4, voo = voo, horario_partida_real=agora,horario_chegada_real=None)

    # voo sem status que terminará a mais de 2 dias de agora
    Voo.objects.create(companhia_aerea='D',horario_partida_previsto=(agora+timedelta(days = 1, hours=22)),horario_chegada_previsto=(agora + timedelta(days = 2, hours=1)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='D')
    ProgressoVoo.objects.create(status_voo = None, voo = voo, horario_partida_real=None,horario_chegada_real=None)

    # voo sem status
    Voo.objects.create(companhia_aerea='C',horario_partida_previsto=(agora-timedelta(minutes = 3)),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='C')
    ProgressoVoo.objects.create(status_voo = None, voo = voo, horario_partida_real=None,horario_chegada_real=None)

def criarTabelasProducaoComRequest(request):
    # reseta_id_voos()
    criarTabelasProducao()
    return render(request, "telainicial.html")

def reseta_id_voos():
    cursor = connection.cursor()

    # Operação de modificação de dado - commit obrigatório
    cursor.execute("UPDATE SQLITE_SEQUENCE SET seq = 0;")
    transaction.commit()
