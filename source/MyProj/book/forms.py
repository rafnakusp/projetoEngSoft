from django import forms
from .models import Voo

class formularioCadastroVoo(forms.Form):
    companhia = forms.CharField(max_length=50, required=False)
    horario_partida = forms.DateTimeField(required=False)
    horario_chegada = forms.DateTimeField(required=False)
    rota = forms.CharField(max_length=50, required=False)
    chegada = forms.BooleanField(label="O destino é este aeroporto?", required=False)

class FormularioFiltroRelatorio(forms.Form):
    timestamp_min = forms.DateTimeField(label="O voo terminou depois de:", required=False)
    timestamp_max = forms.DateTimeField(label="O voo terminou antes de:", required=False)