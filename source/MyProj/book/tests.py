from datetime import datetime, timedelta
from django.utils import timezone
from django.test import TestCase

# Create your tests here.
from book.models import Rota, Voo, Status, ProgressoVoo
from book.views import ControladorAtualizarStatusDeVoo, ControladorCrud, PainelDeMonitoracao, criarTabelasProducao


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
    Voo.objects.create(companhia_aerea='American Airlines',horario_partida_previsto=datetime(2022, 8, 11, 10, 30, tzinfo=timezone.utc),horario_chegada_previsto=datetime(2022, 8, 11, 12, 15, tzinfo=timezone.utc), rota_voo = rota_1)

  def test_criacao_id(self):
    voo_1 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual(voo_1.voo_id, 1)
    self.assertEqual(voo_1.companhia_aerea, 'American Airlines')
    self.assertEqual(voo_1.horario_partida_previsto.strftime('%H:%M, %d of %B, %Y'), '10:30, 11 of August, 2022')
    self.assertEqual(voo_1.horario_chegada_previsto.strftime('%H:%M, %d of %B, %Y'), '12:15, 11 of August, 2022')
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
    self.assertEqual(voo_1.horario_partida_previsto.strftime('%H:%M, %d of %B, %Y'), '10:30, 11 of August, 2022')
    voo_1.horario_partida_previsto = datetime(2022, 9, 15, 10, 30, tzinfo=timezone.utc)
    voo_1.save()
    voo_2 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual(voo_2.horario_partida_previsto.strftime('%H:%M, %d of %B, %Y'), '10:30, 15 of September, 2022')

  def test_update_horario_chegada_previsto(self):
    voo_1 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual(voo_1.horario_chegada_previsto.strftime('%H:%M, %d of %B, %Y'), '12:15, 11 of August, 2022')
    voo_1.horario_chegada_previsto = datetime(2022, 8, 13, 10, 30, tzinfo=timezone.utc)
    voo_1.save()
    voo_2 = Voo.objects.get(companhia_aerea='American Airlines')
    self.assertEqual(voo_2.horario_chegada_previsto.strftime('%H:%M, %d of %B, %Y'), '10:30, 13 of August, 2022')

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
    Voo.objects.create(companhia_aerea='American Airlines',horario_partida_previsto=datetime(2022, 8, 11, 10, 30, tzinfo=timezone.utc),horario_chegada_previsto=datetime(2022, 8, 11, 12, 15, tzinfo=timezone.utc), rota_voo = rota_1)
    voo = Voo.objects.get(companhia_aerea='American Airlines')
    Status.objects.create(status_nome='Em voo')
    status = Status.objects.get(status_nome='Em voo')
    ProgressoVoo.objects.create(status_voo = status, voo = voo, horario_partida_real=datetime(2022, 8, 11, 10, 42, tzinfo=timezone.utc),horario_chegada_real=datetime(2022, 8, 11, 12, 40, tzinfo=timezone.utc))

  def test_criacao_id(self):
    progresso_1 = ProgressoVoo.objects.get(voo_id=1)
    self.assertEqual(progresso_1.voo.voo_id, 1)
    self.assertEqual(progresso_1.voo.companhia_aerea, 'American Airlines')
    self.assertEqual(progresso_1.voo.horario_partida_previsto.strftime('%H:%M, %d of %B, %Y'), '10:30, 11 of August, 2022')
    self.assertEqual(progresso_1.voo.horario_chegada_previsto.strftime('%H:%M, %d of %B, %Y'), '12:15, 11 of August, 2022')
    self.assertEqual(progresso_1.voo.rota_voo.rota_id, 1)
    self.assertEqual(progresso_1.voo.rota_voo.outro_aeroporto, 'Santos Dumont')
    self.assertTrue(progresso_1.voo.rota_voo.chegada)
    self.assertEqual(progresso_1.horario_partida_real.strftime('%H:%M, %d of %B, %Y'), '10:42, 11 of August, 2022')
    self.assertEqual(progresso_1.horario_chegada_real.strftime('%H:%M, %d of %B, %Y'), '12:40, 11 of August, 2022')


################################################################################
####                             CRUD                                       ####
################################################################################

class ControladorCrudTest(TestCase):

  controladorCrud = ControladorCrud()

  @classmethod
  def setUpTestData(cls):
    criarTabelasProducao()

  def test_create_voo(self):

    dados_voo = {
      "companhia_aerea": "American Airlines", 
      "horario_partida_previsto": "2022-10-29 20:07:21.973675+00:00", 
      "horario_chegada_previsto": "2022-10-29 22:57:21.973675+00:00", 
      "rota_voo": "GRU",
    }

    self.controladorCrud.createVoo(companhia=dados_voo["companhia_aerea"], partida=dados_voo["horario_partida_previsto"], chegada=dados_voo["horario_partida_previsto"], rota_str=dados_voo["rota_voo"])
    rota = Rota.objects.get(outro_aeroporto=dados_voo["rota_voo"])
    voo_filtrado = Voo.objects.filter(companhia_aerea=dados_voo["companhia_aerea"], horario_partida_previsto=dados_voo["horario_partida_previsto"], horario_chegada_previsto=dados_voo["horario_partida_previsto"], rota_voo=rota)

    self.assertTrue(voo_filtrado.exists())


################################################################################
####          Atualizar o status de voos/ Painel de Monitoração             ####
################################################################################

# class PainelDeMonitoracaoTest():
  
#   @classmethod
#   def setUpTestData(cls):
#     Rota.objects.create(outro_aeroporto='Santos Dumont',chegada=True)
#     rota_1 = Rota.objects.get(outro_aeroporto='Santos Dumont')
#     Rota.objects.create(outro_aeroporto='GRU',chegada=False)
#     Voo.objects.create(companhia_aerea='American Airlines',horario_partida_previsto=datetime(2022, 8, 11, 10, 30, tzinfo=timezone.utc),horario_chegada_previsto=datetime(2022, 8, 11, 12, 15, tzinfo=timezone.utc), rota_voo = rota_1)
#     voo = Voo.objects.get(companhia_aerea='American Airlines')
#     Status.objects.create(status_nome='Em voo')
#     status = Status.objects.get(status_nome='Em voo')
#     ProgressoVoo.objects.create(status_voo = status, voo = voo, horario_partida_real=datetime(2022, 8, 11, 10, 42, tzinfo=timezone.utc),horario_chegada_real=datetime(2022, 8, 11, 12, 40, tzinfo=timezone.utc))
  
#   def test_atualizar_voo(self):
#     progresso_1 = ProgressoVoo.objects.get(voo_id=1)
#     self.assertEqual(progresso_1.voo.voo_id, 1)

class ControladorAtualizarStatusDeVooTest(TestCase):
  @classmethod
  def setUpTestData(cls):
    agora = datetime.now(tz=timezone.utc)
    print(agora)
    # rotas
    Rota.objects.create(outro_aeroporto='Santos Dumont',chegada=True)
    Rota.objects.create(outro_aeroporto='GRU',chegada=False)

    # status
    Status.objects.create(status_nome='Em voo')
    Status.objects.create(status_nome='Cancelado')
    Status.objects.create(status_nome='Aterrisado')
    Status.objects.create(status_nome='Embarque')
    Status.objects.create(status_nome='Programado')
    Status.objects.create(status_nome='Taxiando')
    Status.objects.create(status_nome='Pronto')
    Status.objects.create(status_nome='Autorizado')

    # voo em progresso (diferente de 'cancelado' ou 'aterrisado')
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
    status4 = Status.objects.get(status_nome='Embarque')
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

  def test_apresentacao_voos(self):
    agora = datetime.now(tz=timezone.utc)
    #controlador
    controlador = ControladorAtualizarStatusDeVoo()
    voos = controlador.apresentaVoosNaoFinalizados()
    
    #verifica se os voos cancelado(id=3) e aterrisado(id=5) a mais de 1 hora não estão na lista
    for voo in voos:
      hcr = datetime(1, 1, 1, 0, 0, tzinfo=timezone.utc) if voo.get('horario_chegada_real')=='-' else datetime.strptime(voo.get('horario_chegada_real'), '%H:%M')
      hcr = hcr if voo.get('horario_chegada_real')=='-' else datetime(agora.year, agora.month, agora.day, hcr.hour, hcr.minute, tzinfo=timezone.utc)
      hpp = datetime.strptime(voo.get('horario_partida_previsto'), '%H:%M')
      hpp = datetime(agora.year, agora.month, agora.day, hpp.hour, hpp.minute, tzinfo=timezone.utc)
      self.assertFalse((voo.get('status') == 'Aterrisado') & (agora - timedelta(hours=1) >= hcr)) #testa se não existem voos aterrisados a mais de 1 hora (não devem haver)
      self.assertFalse((voo.get('status') == 'Cancelado') & (agora - timedelta(hours=1) >= hpp)) #testa se não existem voos cancelados a mais de 1 hora (não devem haver)
      self.assertNotIn(voo.get('voo_id'), [3, 5])
      self.assertTrue((voo.get('status') not in ['Em voo', 'Aterrisado']) & (voo.get('horario_partida_real') == voo.get('horario_chegada_real') == '-') | ((voo.get('status') == 'Em voo') & (voo.get('horario_partida_real') != voo.get('horario_chegada_real') == '-')) | ((voo.get('status') == 'Aterrisado') & (voo.get('horario_partida_real') != voo.get('horario_chegada_real') != '-')))

    

