from django.db import models
import datetime

# Create your models here.

class Rota(models.Model):
  rota_id = models.AutoField(primary_key=True)
  outro_aeroporto = models.CharField(max_length=50, null=False)
  chegada = models.BooleanField(null=False)
  def __str__(self):
    if self.chegada == False:
      return f"Deste aeroporto até {self.outro_aeroporto}"
    else:
      return f"De {self.outro_aeroporto} até este aeroporto"

  class Meta:
    db_table = 'rota'

class Voo(models.Model):
    voo_id = models.AutoField(primary_key=True)
    companhia_aerea = models.CharField(max_length=255, null=False)
    horario_partida_previsto = models.DateTimeField(null=False)
    horario_chegada_previsto = models.DateTimeField(null=False)
    rota_voo = models.ForeignKey(Rota, on_delete=models.CASCADE)
    def __str__(self):
      return f"{self.voo_id}, {self.companhia_aerea}, {self.horario_partida_previsto}, {self.horario_chegada_previsto}, {self.rota_voo}"
    class Meta:
      db_table = 'voo'

class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_nome = models.CharField(max_length=255, null=False)
    class Meta:
        db_table = 'status'

class ProgressoVoo(models.Model):
 progresso_id = models.AutoField(primary_key=True)
 status_voo = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)
 voo = models.ForeignKey(Voo, on_delete=models.CASCADE, null=False)
 horario_partida_real = models.DateTimeField(null=True)
 horario_chegada_real = models.DateTimeField(null=True)
 class Meta:
   db_table = 'progressoVoo' 