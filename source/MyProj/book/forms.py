from django import forms
from .models import Voo

class formularioCadastroVoo(forms.Form):
    companhia = forms.CharField(max_length=50, required=False)
    horario_partida = forms.DateTimeField(required=False)
    horario_chegada = forms.DateTimeField(required=False)
    rota = forms.CharField(max_length=50, required=False)