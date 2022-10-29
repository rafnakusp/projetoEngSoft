from django import forms
from .models import Voo

class formularioCadastroVoo(forms.Form):
    companhia = forms.CharField(max_length=50)
    horario_partida = forms.DateTimeField()
    horario_chegada = forms.DateTimeField()
    rota = forms.CharField(max_length=50)