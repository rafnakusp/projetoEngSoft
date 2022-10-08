from datetime import datetime
from django.utils import timezone
from django.test import TestCase

# Create your tests here.
from book.models import Rota, Voo, Status, ProgressoVoo


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