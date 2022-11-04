from datetime import datetime, timedelta
from django.utils import timezone
from django.test import TestCase, Client

# Create your tests here.
from book.models import Rota, Voo, Status, ProgressoVoo
from book.views import ControladorAtualizarStatusDeVoo, ControladorCrud, PainelDeMonitoracao, ControleGeracaoRelatorios, FronteiraCrud, tz
from book.forms import formularioCadastroVoo, formularioFiltroVoo, FormularioFiltroRelatorioVoosRealizados


class RotaModelTest(TestCase):
 
  @classmethod
  def setUpTestData(cls):
    Rota.objects.create(outro_aeroporto='GRU',chegada=True)

  def test_criacao_id(self):
    rota_1 = Rota.objects.get(outro_aeroporto='GRU')
    self.assertEqual(rota_1.rota_id, 1)
    self.assertEqual(rota_1.outro_aeroporto, 'GRU')
    self.assertTrue(rota_1.chegada)

  def test_update_chegada(self):
    rota_1 = Rota.objects.get(outro_aeroporto='GRU')
    rota_1.chegada = False
    rota_1.save()
    rota_2 = Rota.objects.get(outro_aeroporto='GRU')
    self.assertFalse(rota_2.chegada)

  def test_update_outro_aeroporto(self):
    rota_1 = Rota.objects.get(outro_aeroporto='GRU')
    rota_1.outro_aeroporto = 'Congonhas'
    rota_1.save()
    rota_2 = Rota.objects.get(outro_aeroporto='Congonhas')
    self.assertEqual(rota_2.outro_aeroporto, 'Congonhas')
    with self.assertRaises(Rota.DoesNotExist):
       rota_2 = Rota.objects.get(outro_aeroporto='GRU')

  def test_delete_rota(self):
    rota_1 = Rota.objects.filter(outro_aeroporto='GRU')
    self.assertEqual(Rota.objects.count(), 1)
    rota_1.delete()
    with self.assertRaises(Rota.DoesNotExist):
       rota_2 = Rota.objects.get(outro_aeroporto='GRU')
    self.assertEqual(Rota.objects.count(), 0)


class VooModelTest(TestCase):

  @classmethod
  def setUpTestData(cls):
    Rota.objects.create(outro_aeroporto='Santos Dumont',chegada=True)
    rota_1 = Rota.objects.get(outro_aeroporto='Santos Dumont')
    Rota.objects.create(outro_aeroporto='GRU',chegada=False)
    Voo.objects.create(companhia_aerea='American Airlines',horario_partida_previsto=datetime(2022, 8, 11, 10, 30, tzinfo=tz),horario_chegada_previsto=datetime(2022, 8, 11, 12, 15, tzinfo=tz), rota_voo = rota_1)

  def test_criacao_id(self):
    voo_1 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual(voo_1.voo_id, 1)
    self.assertEqual(voo_1.companhia_aerea, 'American Airlines')
    self.assertEqual((voo_1.horario_partida_previsto-timedelta(hours=3)).strftime('%H:%M, %d of %B, %Y'), '10:30, 11 of August, 2022')
    self.assertEqual((voo_1.horario_chegada_previsto-timedelta(hours=3)).strftime('%H:%M, %d of %B, %Y'), '12:15, 11 of August, 2022')
    self.assertEqual(voo_1.rota_voo.rota_id, 1)
    self.assertEqual(voo_1.rota_voo.outro_aeroporto, 'Santos Dumont')
    self.assertTrue(voo_1.rota_voo.chegada)
  

  def test_update_companhia_aerea(self):
    voo_1 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual(voo_1.companhia_aerea, 'American Airlines')
    voo_1.companhia_aerea = 'Azul'
    voo_1.save()
    with self.assertRaises(Voo.DoesNotExist):
       voo_2 = Voo.objects.get(companhia_aerea='American Airlines')
    voo_2 = Voo.objects.get(companhia_aerea='Azul')
    self.assertEqual(voo_2.companhia_aerea, 'Azul')

  def test_update_horario_partida_previsto(self):
    voo_1 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual((voo_1.horario_partida_previsto-timedelta(hours=3)).strftime('%H:%M, %d of %B, %Y'), '10:30, 11 of August, 2022')
    voo_1.horario_partida_previsto = datetime(2022, 9, 15, 10, 30, tzinfo=tz)
    voo_1.save()
    voo_2 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual((voo_2.horario_partida_previsto-timedelta(hours=3)).strftime('%H:%M, %d of %B, %Y'), '10:30, 15 of September, 2022')

  def test_update_horario_chegada_previsto(self):
    voo_1 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual((voo_1.horario_chegada_previsto-timedelta(hours=3)).strftime('%H:%M, %d of %B, %Y'), '12:15, 11 of August, 2022')
    voo_1.horario_chegada_previsto = datetime(2022, 8, 13, 10, 30, tzinfo=tz)
    voo_1.save()
    voo_2 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual((voo_2.horario_chegada_previsto-timedelta(hours=3)).strftime('%H:%M, %d of %B, %Y'), '10:30, 13 of August, 2022')

  def test_update_rota(self):
    voo_1 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual(voo_1.rota_voo.rota_id, 1)
    self.assertEqual(voo_1.rota_voo.outro_aeroporto, 'Santos Dumont')
    self.assertTrue(voo_1.rota_voo.chegada)
    voo_1.rota_voo = Rota.objects.get(outro_aeroporto='GRU')
    voo_1.save()
    voo_2 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual(voo_1.rota_voo.rota_id, 2)
    self.assertEqual(voo_1.rota_voo.outro_aeroporto, 'GRU')
    self.assertFalse(voo_1.rota_voo.chegada)

  def test_delete_voo(self):
    voo_1 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual(Voo.objects.count(), 1)
    voo_1.delete()
    with self.assertRaises(Voo.DoesNotExist):
       voo_2 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual(Voo.objects.count(), 0)
  

class StatusModelTest(TestCase):
 
  @classmethod
  def setUpTestData(cls):
    Status.objects.create(status_nome='Em voo')

  def test_criacao_id(self):
    status_1 = Status.objects.get(status_nome='Em voo')
    self.assertEqual(status_1.status_id, 1)
    self.assertEqual(status_1.status_nome, 'Em voo')

  def test_update_status_nome(self):
    status_1 = Status.objects.get(status_nome='Em voo')
    status_1.status_nome = 'Taxiando'
    status_1.save()
    status_2 = Status.objects.get(status_id=1)
    self.assertEquals(status_2.status_nome, 'Taxiando')

  def test_delete_status(self):
    status_1 = Status.objects.filter(status_nome='Em voo')
    self.assertEqual(Status.objects.count(), 1)
    status_1.delete()
    with self.assertRaises(Status.DoesNotExist):
       status_2 = Status.objects.get(status_nome='Em voo')
    self.assertEqual(Status.objects.count(), 0)


class ProgressoVooModelTest(TestCase):
 
  @classmethod
  def setUpTestData(cls):
    Rota.objects.create(outro_aeroporto='Santos Dumont',chegada=True)
    rota_1 = Rota.objects.get(outro_aeroporto='Santos Dumont')
    Rota.objects.create(outro_aeroporto='GRU',chegada=False)
    Voo.objects.create(companhia_aerea='American Airlines',horario_partida_previsto=datetime(2022, 8, 11, 10, 30, tzinfo=tz),horario_chegada_previsto=datetime(2022, 8, 11, 12, 15, tzinfo=tz), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='American Airlines')
    Status.objects.create(status_nome='Em voo')
    status = Status.objects.get(status_nome='Em voo')
    ProgressoVoo.objects.create(status_voo = status, voo = voo, horario_partida_real=datetime(2022, 8, 11, 10, 42, tzinfo=tz),horario_chegada_real=datetime(2022, 8, 11, 12, 40, tzinfo=tz))

  def test_criacao_id(self):
    progresso_1 = ProgressoVoo.objects.get(voo_id=1)
    self.assertEqual(progresso_1.voo.voo_id, 1)
    self.assertEqual(progresso_1.voo.companhia_aerea, 'American Airlines')
    self.assertEqual((progresso_1.voo.horario_partida_previsto-timedelta(hours=3)).strftime('%H:%M, %d of %B, %Y'), '10:30, 11 of August, 2022')
    self.assertEqual((progresso_1.voo.horario_chegada_previsto-timedelta(hours=3)).strftime('%H:%M, %d of %B, %Y'), '12:15, 11 of August, 2022')
    self.assertEqual(progresso_1.voo.rota_voo.rota_id, 1)
    self.assertEqual(progresso_1.voo.rota_voo.outro_aeroporto, 'Santos Dumont')
    self.assertTrue(progresso_1.voo.rota_voo.chegada)
    self.assertEqual((progresso_1.horario_partida_real-timedelta(hours=3)).strftime('%H:%M, %d of %B, %Y'), '10:42, 11 of August, 2022')
    self.assertEqual((progresso_1.horario_chegada_real-timedelta(hours=3)).strftime('%H:%M, %d of %B, %Y'), '12:40, 11 of August, 2022')

################################################################################
################################################################################
################################################################################
####                           Caso de uso: CRUD                            ####
################################################################################
################################################################################
################################################################################

class ControladorCrudTest(TestCase):
  formatodata = "%Y-%m-%dT%H:%M"

  controladorCrud = ControladorCrud()
  fronteiraCrud = FronteiraCrud()

  @classmethod
  def setUpTestData(cls):
    criarTabelasTestes()
    agora = datetime.now(tz=tz)
    rota = Rota.objects.get(outro_aeroporto='GRU')
    Voo.objects.create(companhia_aerea='Azul',horario_partida_previsto=(agora + timedelta(days = 2)),horario_chegada_previsto=(agora + timedelta(days = 2, hours=5)), rota_voo = rota)

    rota = Rota.objects.create(outro_aeroporto='Congonhas',chegada=False)
    Voo.objects.create(companhia_aerea='Avianca',horario_partida_previsto=(agora + timedelta(days = 4)),horario_chegada_previsto=(agora + timedelta(days = 4, hours=6)), rota_voo = rota)

  def test_create_voo(self):
    agora = datetime.now(tz=tz)
    
    # Voo sem erros
    dados_voo = {
      "companhia": "American Airlines", 
      "horario_partida": (agora+timedelta(days=1)).strftime(self.formatodata), 
      "horario_chegada": (agora+timedelta(hours=28)).strftime(self.formatodata), 
      "rota": "GRU",
    }
    form = formularioCadastroVoo(dados_voo)
    voo_criado = self.controladorCrud.createVoo(form)
    rota = Rota.objects.get(outro_aeroporto=dados_voo["rota"], chegada = True if 'chegada' in form.data else False)
    voo_filtrado = Voo.objects.filter(companhia_aerea=dados_voo["companhia"], horario_partida_previsto=datetime.strptime(dados_voo['horario_partida'], self.formatodata).replace(tzinfo=tz), horario_chegada_previsto=datetime.strptime(dados_voo['horario_chegada'], self.formatodata).replace(tzinfo=tz), rota_voo=rota)
    self.assertTrue(voo_filtrado.exists())
    self.assertIsInstance(voo_criado, Voo)
    self.assertSequenceEqual([voo_criado.companhia_aerea, voo_criado.rota_voo.outro_aeroporto, voo_criado.rota_voo.chegada],\
      ["American Airlines", "GRU", False])
    self.assertTrue(abs(voo_criado.horario_partida_previsto - (agora+timedelta(days=1))) < timedelta(minutes=1))
    self.assertTrue(abs(voo_criado.horario_chegada_previsto - (agora+timedelta(hours=28))) < timedelta(minutes=1))

    # Voo com rota errada
    dados_voo = {
      "companhia": "American Airlines", 
      "horario_partida": (agora+timedelta(days=1)).strftime(self.formatodata), 
      "horario_chegada": (agora+timedelta(hours=28)).strftime(self.formatodata), 
      "rota": "GRU",
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    voo_criado = self.controladorCrud.createVoo(form)
    rota = Rota.objects.filter(outro_aeroporto=dados_voo["rota"], chegada = True if 'chegada' in form.data else False)
    voo_filtrado = Voo.objects.filter(companhia_aerea=dados_voo["companhia"], horario_partida_previsto=datetime.strptime(dados_voo['horario_partida'], self.formatodata).replace(tzinfo=tz), horario_chegada_previsto=datetime.strptime(dados_voo['horario_chegada'], self.formatodata).replace(tzinfo=tz), rota_voo=rota if rota.exists() else None)
    self.assertFalse(rota.exists())
    self.assertFalse(voo_filtrado.exists())
    self.assertIsInstance(voo_criado, str)
    self.assertEqual(voo_criado, "rota_errada")

    # Voo data de chegada antes da de partida
    dados_voo = {
      "companhia": "American Airlines", 
      "horario_partida": (agora+timedelta(days=1)).strftime(self.formatodata), 
      "horario_chegada": (agora+timedelta(hours=23)).strftime(self.formatodata), 
      "rota": "Santos Dumont",
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    voo_criado = self.controladorCrud.createVoo(form)
    rota = Rota.objects.get(outro_aeroporto=dados_voo["rota"], chegada = True if 'chegada' in form.data else False)
    voo_filtrado = Voo.objects.filter(companhia_aerea=dados_voo["companhia"], horario_partida_previsto=datetime.strptime(dados_voo['horario_partida'], self.formatodata).replace(tzinfo=tz), horario_chegada_previsto=datetime.strptime(dados_voo['horario_chegada'], self.formatodata).replace(tzinfo=tz), rota_voo=rota)
    self.assertFalse(voo_filtrado.exists())
    self.assertIsInstance(voo_criado, str)
    self.assertEqual(voo_criado, "chegada antes da partida")

    # Voo data de chegada no passado
    dados_voo = {
      "companhia": "American Airlines", 
      "horario_partida": (agora-timedelta(days=1)).strftime(self.formatodata), 
      "horario_chegada": (agora-timedelta(hours=23)).strftime(self.formatodata), 
      "rota": "Santos Dumont",
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    voo_criado = self.controladorCrud.createVoo(form)
    rota = Rota.objects.get(outro_aeroporto=dados_voo["rota"], chegada = True if 'chegada' in form.data else False)
    voo_filtrado = Voo.objects.filter(companhia_aerea=dados_voo["companhia"], horario_partida_previsto=datetime.strptime(dados_voo['horario_partida'], self.formatodata).replace(tzinfo=tz), horario_chegada_previsto=datetime.strptime(dados_voo['horario_chegada'], self.formatodata).replace(tzinfo=tz), rota_voo=rota)
    self.assertFalse(voo_filtrado.exists())
    self.assertIsInstance(voo_criado, str)
    self.assertEqual(voo_criado, "horario chegada no passado")

    # Voo data de partida no passado
    dados_voo = {
      "companhia": "American Airlines", 
      "horario_partida": (agora-timedelta(hours=1)).strftime(self.formatodata), 
      "horario_chegada": (agora+timedelta(hours=17)).strftime(self.formatodata), 
      "rota": "Santos Dumont",
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    voo_criado = self.controladorCrud.createVoo(form)
    rota = Rota.objects.get(outro_aeroporto=dados_voo["rota"], chegada = True if 'chegada' in form.data else False)
    voo_filtrado = Voo.objects.filter(companhia_aerea=dados_voo["companhia"], horario_partida_previsto=datetime.strptime(dados_voo['horario_partida'], self.formatodata).replace(tzinfo=tz), horario_chegada_previsto=datetime.strptime(dados_voo['horario_chegada'], self.formatodata).replace(tzinfo=tz), rota_voo=rota)
    self.assertFalse(voo_filtrado.exists())
    self.assertIsInstance(voo_criado, str)
    self.assertEqual(voo_criado, "horario partida no passado")

    # Voo duração maior que 20 horas
    dados_voo = {
      "companhia": "American Airlines", 
      "horario_partida": (agora+timedelta(hours=1)).strftime(self.formatodata), 
      "horario_chegada": (agora+timedelta(hours=22)).strftime(self.formatodata), 
      "rota": "Santos Dumont",
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    voo_criado = self.controladorCrud.createVoo(form)
    rota = Rota.objects.get(outro_aeroporto=dados_voo["rota"], chegada = True if 'chegada' in form.data else False)
    voo_filtrado = Voo.objects.filter(companhia_aerea=dados_voo["companhia"], horario_partida_previsto=datetime.strptime(dados_voo['horario_partida'], self.formatodata).replace(tzinfo=tz), horario_chegada_previsto=datetime.strptime(dados_voo['horario_chegada'], self.formatodata).replace(tzinfo=tz), rota_voo=rota)
    self.assertFalse(voo_filtrado.exists())
    self.assertIsInstance(voo_criado, str)
    self.assertEqual(voo_criado, "voo muito longo")

  def test_read_voos_campos_preenchidos(self):
    
    dados_voo = {
      "companhia": "American Airlines",
      "intervalo_partida_0": "",
      "intervalo_partida_1": "2022-08-11T10:30",
      "intervalo_chegada_0": "",
      "intervalo_chegada_1": "2022-08-11T12:15", 
      "rota": "Santos Dumont",
      "chegada": True,
    }

    form = formularioFiltroVoo(dados_voo)
    
    voos = self.controladorCrud.readVoos(form)

    self.assertEqual(1, len(voos))

  def test_read_voos_campos_em_branco(self):
    
    dados_voo = {
      "companhia": "", 
      "intervalo_partida_0": "",
      "intervalo_partida_1": "",
      "intervalo_chegada_0": "",
      "intervalo_chegada_1": "", 
      "rota": "",
    }

    form = formularioFiltroVoo(dados_voo)
    
    voos = self.controladorCrud.readVoos(form)

    self.assertEqual(14, len(voos))

  def test_read_voos_alguns_em_branco(self):
    dados_voo = {
      "companhia": "", 
      "intervalo_partida_0": "",
      "intervalo_partida_1": "",
      "intervalo_chegada_0": "",
      "intervalo_chegada_1": "", 
      "rota": "GRU",
    }

    form = formularioFiltroVoo(dados_voo)
    
    voos = self.controladorCrud.readVoos(form)

    self.assertEqual(7, len(voos))

    dados_voo = {
      "companhia": "Azul", 
      "intervalo_partida_0": "",
      "intervalo_partida_1": "",
      "intervalo_chegada_0": "",
      "intervalo_chegada_1": "", 
      "rota": "GRU",
    }

    form = formularioFiltroVoo(dados_voo)
    
    voos = self.controladorCrud.readVoos(form)

    self.assertEqual(2, len(voos))

  def test_read_rota_inexistente(self):
    dados_voo = {
      "companhia": "", 
      "intervalo_partida_0": "",
      "intervalo_partida_1": "",
      "intervalo_chegada_0": "",
      "intervalo_chegada_1": "", 
      "rota": "GRU",
      "chegada": True
    }

    form = formularioFiltroVoo(dados_voo)
  
    voos = self.controladorCrud.readVoos(form)

    self.assertIsNone(voos)

  def test_read_intervalos(self):
    agora = datetime.now(tz=tz)
    #Teste inicio intervalo partida
    dados_voo = {
      "companhia": "", 
      "intervalo_partida_0": datetime.strftime(agora, self.formatodata),
      "intervalo_partida_1": "",
      "intervalo_chegada_0": "",
      "intervalo_chegada_1": "", 
      "rota": "",
    }

    form = formularioFiltroVoo(dados_voo)
    
    voos = self.controladorCrud.readVoos(form)

    self.assertEqual(7, len(voos))

    #Teste intervalo partida
    dados_voo = {
      "companhia": "", 
      "intervalo_partida_0": datetime.strftime((agora+timedelta(minutes=18)), self.formatodata),
      "intervalo_partida_1": datetime.strftime((agora+timedelta(days=3)), self.formatodata),
      "intervalo_chegada_0": "",
      "intervalo_chegada_1": "", 
      "rota": "",
    }

    form = formularioFiltroVoo(dados_voo)
    
    voos = self.controladorCrud.readVoos(form)

    self.assertEqual(3, len(voos))

    #Teste inicio intervalo chegada
    dados_voo = {
      "companhia": "", 
      "intervalo_partida_0": "",
      "intervalo_partida_1": "",
      "intervalo_chegada_0": datetime.strftime(agora, self.formatodata),
      "intervalo_chegada_1": "", 
      "rota": "",
    }

    form = formularioFiltroVoo(dados_voo)
    
    voos = self.controladorCrud.readVoos(form)

    self.assertEqual(11, len(voos))

    #Teste intervalo chegada
    dados_voo = {
      "companhia": "", 
      "intervalo_partida_0": "",
      "intervalo_partida_1": "",
      "intervalo_chegada_0": datetime.strftime(agora+timedelta(hours=3, minutes=50), self.formatodata),
      "intervalo_chegada_1": datetime.strftime((agora+timedelta(days=3)), self.formatodata), 
      "rota": "",
    }

    form = formularioFiltroVoo(dados_voo)
    
    voos = self.controladorCrud.readVoos(form)

    self.assertEqual(2, len(voos))

    #Teste fim intervalos partida e chegada
    dados_voo = {
      "companhia": "", 
      "intervalo_partida_0": "",
      "intervalo_partida_1": datetime.strftime((agora+timedelta(hours=20)), self.formatodata),
      "intervalo_chegada_0": "",
      "intervalo_chegada_1": datetime.strftime((agora+timedelta(days=1)), self.formatodata), 
      "rota": "",
    }

    form = formularioFiltroVoo(dados_voo)
    
    voos = self.controladorCrud.readVoos(form)

    self.assertEqual(11, len(voos))

    #Teste intervalos partida e chegada
    dados_voo = {
      "companhia": "", 
      "intervalo_partida_0": datetime.strftime(agora-timedelta(minutes=10), self.formatodata),
      "intervalo_partida_1": datetime.strftime((agora+timedelta(hours=20)), self.formatodata),
      "intervalo_chegada_0": datetime.strftime(agora+timedelta(hours=3), self.formatodata),
      "intervalo_chegada_1": datetime.strftime((agora+timedelta(days=1)), self.formatodata), 
      "rota": "",
    }

    form = formularioFiltroVoo(dados_voo)
    
    voos = self.controladorCrud.readVoos(form)

    self.assertEqual(6, len(voos))


  def test_delete(self):
    vooid = 3
    
    self.controladorCrud.deleteVoosPorId(vooid)
    queryset_vooid = Voo.objects.all().filter(voo_id=vooid)

    self.assertEqual(0, queryset_vooid.count())

  def test_update(self):
    agora = datetime.now(tz=tz)
    voo = Voo.objects.select_related("rota_voo").get(voo_id='1')

    # Formulario sem erros
    dados_voo = {
      "companhia": "New Airlines", 
      "horario_partida": datetime.strftime(voo.horario_partida_previsto, self.formatodata), 
      "horario_chegada": datetime.strftime(voo.horario_chegada_previsto, self.formatodata), 
      "rota": voo.rota_voo.outro_aeroporto,
      "chegada": voo.rota_voo.chegada,
    }
    form = formularioCadastroVoo(dados_voo)
    self.assertNotEqual(dados_voo['companhia'], voo.companhia_aerea)
    voo = self.controladorCrud.updateVoo(voo.voo_id, form)
    self.assertEqual(dados_voo['companhia'], voo.companhia_aerea)
    self.assertIsInstance(voo, Voo)

    # rota inexistente
    dados_voo = {
      "companhia": voo.companhia_aerea, 
      "horario_partida": datetime.strftime(voo.horario_partida_previsto, self.formatodata), 
      "horario_chegada": datetime.strftime(voo.horario_chegada_previsto, self.formatodata), 
      "rota": voo.rota_voo.outro_aeroporto,
    }
    form = formularioCadastroVoo(dados_voo)
    self.assertNotEqual(True if 'chegada' in form.data else False, voo.rota_voo.chegada)
    voo_atualizado = self.controladorCrud.updateVoo(voo.voo_id, form)
    rota = Rota.objects.filter(outro_aeroporto=dados_voo["rota"], chegada= True if 'chegada' in form.data else False)
    self.assertFalse(rota.exists())
    self.assertEqual(voo_atualizado, "rota_errada")
    voo = Voo.objects.select_related("rota_voo").get(voo_id='1')
    self.assertNotEqual(True if 'chegada' in form.data else False, voo.rota_voo.chegada)
    self.assertIsInstance(voo_atualizado, str)

    # Voo data de chegada antes da de partida
    dados_voo = {
      "companhia": voo.companhia_aerea, 
      "horario_partida": (agora+timedelta(days=1)).strftime(self.formatodata), 
      "horario_chegada": (agora+timedelta(hours=23)).strftime(self.formatodata), 
      "rota": voo.rota_voo.outro_aeroporto,
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    self.assertNotEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertNotEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))
    voo_atualizado = self.controladorCrud.updateVoo(voo.voo_id, form)
    self.assertIsInstance(voo_atualizado, str)
    self.assertEqual(voo_atualizado, "chegada antes da partida")
    voo = Voo.objects.select_related("rota_voo").get(voo_id='1')
    self.assertNotEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertNotEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))

    # Voo data de chegada e de partida no passado e datas antigas também no passado - deve mudar ambas as datas
    dados_voo = {
      "companhia": voo.companhia_aerea, 
      "horario_partida": (agora-timedelta(days=1)).strftime(self.formatodata), 
      "horario_chegada": (agora-timedelta(hours=23)).strftime(self.formatodata), 
      "rota": voo.rota_voo.outro_aeroporto,
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    self.assertNotEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertNotEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))
    voo = self.controladorCrud.updateVoo(voo.voo_id, form)
    self.assertIsInstance(voo, Voo)
    self.assertEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))

    # Mudar chegada para futuro
    dados_voo = {
      "companhia": voo.companhia_aerea, 
      "horario_partida": (agora-timedelta(hours=1)).strftime(self.formatodata), 
      "horario_chegada": (agora+timedelta(hours=12)).strftime(self.formatodata), 
      "rota": voo.rota_voo.outro_aeroporto,
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    self.assertNotEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertNotEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))
    voo = self.controladorCrud.updateVoo(voo.voo_id, form)
    self.assertIsInstance(voo, Voo)
    self.assertEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))

    # Voo data de chegada no passado, antes no futuro, não faz update
    dados_voo = {
      "companhia": voo.companhia_aerea, 
      "horario_partida": (agora-timedelta(minutes=50)).strftime(self.formatodata), 
      "horario_chegada": (agora-timedelta(minutes=23)).strftime(self.formatodata), 
      "rota": voo.rota_voo.outro_aeroporto,
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    self.assertNotEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertNotEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))
    voo = self.controladorCrud.updateVoo(voo.voo_id, form)
    self.assertIsInstance(voo, str)
    self.assertEqual(voo, "horario chegada no passado")
    voo = Voo.objects.select_related("rota_voo").get(voo_id='1')
    self.assertNotEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertNotEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))

    # Mudar chegada para futuro
    dados_voo = {
      "companhia": "Nova Companhia", 
      "horario_partida": (agora+timedelta(hours=1)).strftime(self.formatodata), 
      "horario_chegada": datetime.strftime(voo.horario_chegada_previsto, self.formatodata), 
      "rota": voo.rota_voo.outro_aeroporto,
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    self.assertNotEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertNotEqual(dados_voo['companhia'], voo.companhia_aerea)
    voo = self.controladorCrud.updateVoo(voo.voo_id, form)
    self.assertIsInstance(voo, Voo)
    self.assertEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertEqual(dados_voo['companhia'], voo.companhia_aerea)

    # Voo data de partida no passado, sendo que estava no futuro
    dados_voo = {
      "companhia": voo.companhia_aerea, 
      "horario_partida": (agora-timedelta(minutes=50)).strftime(self.formatodata), 
      "horario_chegada": (agora+timedelta(minutes=23)).strftime(self.formatodata), 
      "rota": voo.rota_voo.outro_aeroporto,
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    self.assertNotEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertNotEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))
    voo = self.controladorCrud.updateVoo(voo.voo_id, form)
    self.assertIsInstance(voo, str)
    self.assertEqual(voo, "horario partida no passado")
    voo = Voo.objects.select_related("rota_voo").get(voo_id='1')
    self.assertNotEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertNotEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))

    # Voo duração maior que 20 horas
    dados_voo = {
      "companhia": voo.companhia_aerea, 
      "horario_partida": (agora+timedelta(minutes=5)).strftime(self.formatodata), 
      "horario_chegada": (agora+timedelta(hours=22)).strftime(self.formatodata), 
      "rota": voo.rota_voo.outro_aeroporto,
      "chegada": True
    }
    form = formularioCadastroVoo(dados_voo)
    self.assertNotEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertNotEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))
    voo = self.controladorCrud.updateVoo(voo.voo_id, form)
    self.assertIsInstance(voo, str)
    self.assertEqual(voo, "voo muito longo")
    voo = Voo.objects.select_related("rota_voo").get(voo_id='1')
    self.assertNotEqual(dados_voo['horario_partida'], (voo.horario_partida_previsto-timedelta(hours=3)).strftime(self.formatodata))
    self.assertNotEqual(dados_voo['horario_chegada'], (voo.horario_chegada_previsto-timedelta(hours=3)).strftime(self.formatodata))



################################################################################
################################################################################
####         Caso de uso: Atualizar o status de voos/ Painel de Monitoração ####
################################################################################
################################################################################

class ControladorAtualizarStatusDeVooTest(TestCase):
  def __init__(self, methodName: str = ...) -> None:
    self.controlador = ControladorAtualizarStatusDeVoo()
    super().__init__(methodName)

  @classmethod
  def setUpTestData(cls):
    criarTabelasTestes()

  def test_apresentacao_voos(self):
    agora = datetime.now(tz=tz)
    #controlador
    voos = self.controlador.apresentaVoosNaoFinalizados()
    
    #verifica se os voos cancelado(id=3) e Aterrissado(id=5) a mais de 1 hora não estão na lista
    for voo in voos:
      hcr = datetime(1, 1, 1, 0, 0, tzinfo=tz) if voo.horario_chegada_real == None else voo.horario_chegada_real
      status = None if  voo.status_voo == None else voo.status_voo.status_nome
      self.assertFalse((status == 'Aterrissado') & (agora - timedelta(hours=1) >= hcr)) #testa se não existem voos Aterrissados a mais de 1 hora (não devem haver)
      self.assertFalse((status == 'Cancelado') & (agora - timedelta(hours=1) >= voo.voo.horario_partida_previsto)) #testa se não existem voos cancelados a mais de 1 hora (não devem haver)
      self.assertFalse((status == None) & (agora + timedelta(days=2) <= voo.voo.horario_chegada_previsto)) #testa se não existem voos cadastrados que ocorrerão somente em dois dias ou mais (não devem ser monitorados)
      self.assertNotIn(voo.voo_id, [3, 5, 12])
      self.assertTrue((status not in ['Em voo', 'Autorizado', 'Aterrissado']) & (voo.horario_partida_real == voo.horario_chegada_real == None) | ((status in ['Em voo', 'Autorizado']) & (voo.horario_partida_real != voo.horario_chegada_real == None)) | ((status == 'Aterrissado') & (voo.horario_partida_real != voo.horario_chegada_real != '-')))

  def test_status_possiveis(self):
    # status vazio
    vooid = Voo.objects.filter(companhia_aerea='C').values('voo_id')[0]
    status_possiveis = self.controlador.statusPossiveis(vooid.get('voo_id'))
    self.assertListEqual(status_possiveis, [Status.objects.get(status_nome='Embarque'), Status.objects.get(status_nome='Cancelado'), Status.objects.get(status_nome='Em voo')])

    # status 'embarque'
    vooid = Voo.objects.filter(companhia_aerea='American Air').values('voo_id')[0]
    status_possiveis = self.controlador.statusPossiveis(vooid.get('voo_id'))
    self.assertListEqual(status_possiveis, [Status.objects.get(status_nome='Programado'), Status.objects.get(status_nome='Cancelado')])

    # status 'programado'
    vooid = Voo.objects.filter(companhia_aerea='Amer').values('voo_id')[0]
    status_possiveis = self.controlador.statusPossiveis(vooid.get('voo_id'))
    self.assertListEqual(status_possiveis, [Status.objects.get(status_nome='Taxiando'), Status.objects.get(status_nome='Cancelado')])

    # status 'taxiando'
    vooid = Voo.objects.filter(companhia_aerea='American').values('voo_id')[0]
    status_possiveis = self.controlador.statusPossiveis(vooid.get('voo_id'))
    self.assertListEqual(status_possiveis, [Status.objects.get(status_nome='Pronto'), Status.objects.get(status_nome='Cancelado')])

    # status 'pronto'
    vooid = Voo.objects.filter(companhia_aerea='A').values('voo_id')[0]
    status_possiveis = self.controlador.statusPossiveis(vooid.get('voo_id'))
    self.assertListEqual(status_possiveis, [Status.objects.get(status_nome='Autorizado'), Status.objects.get(status_nome='Cancelado')])

    # status 'autorizado'
    vooid = Voo.objects.filter(companhia_aerea='B').values('voo_id')[0]
    status_possiveis = self.controlador.statusPossiveis(vooid.get('voo_id'))
    self.assertListEqual(status_possiveis, [Status.objects.get(status_nome='Em voo')])

    # status 'cancelado'
    vooid = Voo.objects.filter(companhia_aerea='Azul').values('voo_id')[0]
    status_possiveis = self.controlador.statusPossiveis(vooid.get('voo_id'))
    self.assertListEqual(status_possiveis, [])

    # status 'aterrissado'
    vooid = Voo.objects.filter(companhia_aerea='LATAM').values('voo_id')[0]
    status_possiveis = self.controlador.statusPossiveis(vooid.get('voo_id'))
    self.assertListEqual(status_possiveis, [])


  def test_atualizacao_status_voo(self):
    agora = datetime.now(tz=tz)

    # alteração normal (sem alteração de outros campos)
    vooid = Voo.objects.filter(companhia_aerea='C').values('voo_id')[0].get('voo_id')
    pvoo = ProgressoVoo.objects.select_related('status_voo', 'voo').get(voo_id=vooid)
    self.assertIsNone(pvoo.status_voo)
    embarqueid = Status.objects.filter(status_nome='Embarque').values('status_id')[0].get('status_id')
    self.controlador.atualizaStatusDeVoo(vooid, embarqueid)
    pvoo = ProgressoVoo.objects.select_related('status_voo').get(voo_id=vooid)
    self.assertEqual(pvoo.status_voo.status_nome, 'Embarque')

    # alteração para status de 'Autorizado', deve preencher campo de horario_partida_real
    vooid = Voo.objects.filter(companhia_aerea='A').values('voo_id')[0].get('voo_id')
    pvoo = ProgressoVoo.objects.select_related('status_voo', 'voo').get(voo_id=vooid)
    self.assertEqual(pvoo.status_voo.status_nome, 'Pronto')
    self.assertIsNone(pvoo.horario_partida_real)
    self.assertIsNone(pvoo.horario_chegada_real)
    embarqueid = Status.objects.filter(status_nome='Autorizado').values('status_id')[0].get('status_id')
    self.controlador.atualizaStatusDeVoo(vooid, embarqueid)
    pvoo = ProgressoVoo.objects.select_related('status_voo').get(voo_id=vooid)
    self.assertEqual(pvoo.status_voo.status_nome, 'Autorizado')
    self.assertTrue(abs(pvoo.horario_partida_real-agora) < timedelta(seconds=1))
    self.assertIsNone(pvoo.horario_chegada_real)

    # alteração para status de 'Aterrissado', deve preencher campo de horario_chegada_real
    vooid = Voo.objects.filter(companhia_aerea='American Airlines').values('voo_id')[0].get('voo_id')
    pvoo = ProgressoVoo.objects.select_related('status_voo', 'voo').get(voo_id=vooid)
    self.assertEqual(pvoo.status_voo.status_nome, 'Em voo')
    self.assertIsNotNone(pvoo.horario_partida_real)
    self.assertIsNone(pvoo.horario_chegada_real)
    embarqueid = Status.objects.filter(status_nome='Aterrissado').values('status_id')[0].get('status_id')
    self.controlador.atualizaStatusDeVoo(vooid, embarqueid)
    pvoo = ProgressoVoo.objects.select_related('status_voo').get(voo_id=vooid)
    self.assertEqual(pvoo.status_voo.status_nome, 'Aterrissado')
    self.assertIsNotNone(pvoo.horario_partida_real)
    self.assertTrue(abs(pvoo.horario_chegada_real-agora) < timedelta(seconds=1))

################################################################################
################################################################################
####                           Caso de uso: Geração de relatórios           ####
################################################################################
################################################################################

class ControleGeracaoRelatoriosTest(TestCase):
  controleGeracaoRelatorios = ControleGeracaoRelatorios()
  @classmethod
  def setUpTestData(cls):
    criarTabelasTestes()
    status = Status.objects.get(status_nome="Aterrissado")

    Rota.objects.create(outro_aeroporto='Santos Dumont',chegada=True)
    rota = Rota.objects.get(rota_id=1)
    voo = Voo.objects.create(companhia_aerea="A", horario_partida_previsto="2022-08-04 01:30:00+00:00", horario_chegada_previsto="2022-08-04 10:32:00+00:00", rota_voo=rota)
    ProgressoVoo.objects.create(voo=voo, horario_partida_real="2022-08-04 01:50:00+00:00", horario_chegada_real="2022-08-04 10:35:00+00:00", status_voo=status)

    voo = Voo.objects.create(companhia_aerea="B", horario_partida_previsto="2022-08-06 02:30:00+00:00", horario_chegada_previsto="2022-08-06 10:40:00+00:00", rota_voo=rota)
    ProgressoVoo.objects.create(voo=voo, horario_partida_real="2022-08-06 02:37:00+00:00", horario_chegada_real="2022-08-06 10:30:00+00:00", status_voo=status)

    voo = Voo.objects.create(companhia_aerea="B", horario_partida_previsto="2022-08-13 07:53:00+00:00", horario_chegada_previsto="2022-08-13 10:45:00+00:00", rota_voo=rota)
    ProgressoVoo.objects.create(voo=voo, horario_partida_real="2022-08-13 07:50:00+00:00", horario_chegada_real="2022-08-13 10:30:00+00:00", status_voo=status)

    status = Status.objects.get(status_nome="Em voo")
    voo = Voo.objects.create(companhia_aerea="B", horario_partida_previsto="2022-08-13 07:53:00+00:00", horario_chegada_previsto="2022-08-13 10:45:00+00:00", rota_voo=rota)
    ProgressoVoo.objects.create(voo=voo, horario_partida_real="2022-08-13 07:50:00+00:00", horario_chegada_real=None, status_voo=status)

  def test_filtrar_voos(self):
    agora = datetime.now(tz=tz)

    filtro_teste = {
      "companhia": "", 
      "intervalo_partida_0": "",
      "intervalo_partida_1": "2022-08-11T10:30",
      "intervalo_chegada_0": "",
      "intervalo_chegada_1": ""
    }

    form = FormularioFiltroRelatorioVoosRealizados(filtro_teste)

    lista_voos_resultado = self.controleGeracaoRelatorios.filtrarVoos(form)

    self.assertEqual(2, lista_voos_resultado.count())
  
  def test_filtrar_voos_realizados_min_null(self):
    filtro_teste = {
      "companhia": "", 
      "intervalo_partida_0": "",
      "intervalo_partida_1": "",
      "intervalo_chegada_0": "",
      "intervalo_chegada_1": ""
    }

    form = FormularioFiltroRelatorioVoosRealizados(filtro_teste)

    lista_voos_resultado = self.controleGeracaoRelatorios.filtrarVoosRealizados(form)

    self.assertEqual(5, lista_voos_resultado.count())

  def test_filtrar_voos_realizados(self):
    filtro_teste = {
      "companhia": "", 
      "intervalo_partida_0": "",
      "intervalo_partida_1": "",
      "intervalo_chegada_0": "2022-09-11T10:30",
      "intervalo_chegada_1": ""
    }

    form = FormularioFiltroRelatorioVoosRealizados(filtro_teste)

    lista_voos_resultado = self.controleGeracaoRelatorios.filtrarVoosRealizados(form)

    self.assertEqual(2, lista_voos_resultado.count())

  def test_filtrar_voos_atrasados(self):
    filtro_teste = {
      "companhia": "",
      "status": '-'
    }

    lista_voos_resultado = self.controleGeracaoRelatorios.filtrarVoosAtrasados(filtro_teste['status'], filtro_teste["companhia"])

    self.assertEqual(1, lista_voos_resultado.count())

    filtro_teste = {
      "companhia": "",
      "status": ''
    }

    lista_voos_resultado = self.controleGeracaoRelatorios.filtrarVoosAtrasados(filtro_teste['status'], filtro_teste["companhia"])

    self.assertEqual(7, lista_voos_resultado.count())

    filtro_teste = {
      "companhia": "",
      "status": 'Em voo'
    }

    lista_voos_resultado = self.controleGeracaoRelatorios.filtrarVoosAtrasados(filtro_teste['status'], filtro_teste["companhia"])

    self.assertEqual(2, lista_voos_resultado.count())
    
################################################################################
################################################################################
####                    Testes da interface http (requests)                 ####
################################################################################          
################################################################################          

class TesteRequestLogin(TestCase):
  def teste_login_correto(self):
    cliente = Client()

    resposta = cliente.post('/login/', {'username': 'operadordevoos', 'password': 'senha'})

    self.assertEqual(resposta.status_code, 302)

  def teste_login_incorreto(self):
    cliente = Client()

    resposta = cliente.post('/login/', {'username': 'operadodevoos', 'password': 'senha'})

    self.assertEqual(resposta.status_code, 200)


################################################################################
################################################################################
####                         Criador de tabelas                             ####
################################################################################          
################################################################################          

def criarTabelasTestes():
    agora = datetime.now(tz=tz)
    print(agora)
    # rotas
    Rota.objects.create(outro_aeroporto='Santos Dumont',chegada=True)
    Rota.objects.create(outro_aeroporto='GRU',chegada=False)

    # status
    Status.objects.create(status_nome='Em voo')
    Status.objects.create(status_nome='Cancelado')
    Status.objects.create(status_nome='Aterrissado')
    Status.objects.create(status_nome='Embarque')
    Status.objects.create(status_nome='Programado')
    Status.objects.create(status_nome='Taxiando')
    Status.objects.create(status_nome='Pronto')
    Status.objects.create(status_nome='Autorizado')

    # voo em progresso (diferente de 'cancelado' ou 'Aterrissado')
    rota_1 = Rota.objects.get(outro_aeroporto='Santos Dumont')
    Voo.objects.create(companhia_aerea='American Airlines',horario_partida_previsto=datetime(2022, 8, 11, 10, 30, tzinfo=tz),horario_chegada_previsto=datetime(2022, 8, 11, 12, 15, tzinfo=tz), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='American Airlines')
    status = Status.objects.get(status_nome='Em voo')
    ProgressoVoo.objects.create(status_voo = status, voo = voo, horario_partida_real=datetime(2022, 8, 11, 10, 42, tzinfo=tz),horario_chegada_real=None)

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

    # voo sem status que terminará a menos de 2 dias de agora
    Voo.objects.create(companhia_aerea='C',horario_partida_previsto=(agora-timedelta(minutes = 3)),horario_chegada_previsto=(agora + timedelta(minutes = 220)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='C')
    ProgressoVoo.objects.create(status_voo = None, voo = voo, horario_partida_real=None,horario_chegada_real=None)

    # voo sem status que terminará a mais de 2 dias de agora
    Voo.objects.create(companhia_aerea='D',horario_partida_previsto=(agora+timedelta(days = 1, hours=22)),horario_chegada_previsto=(agora + timedelta(days = 2, hours=1)), rota_voo = rota_2)
    voo = Voo.objects.get(companhia_aerea='D')
    ProgressoVoo.objects.create(status_voo = None, voo = voo, horario_partida_real=None,horario_chegada_real=None)
