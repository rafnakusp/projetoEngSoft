from django.forms import DateTimeField, DateTimeInput, CharField, Form, BooleanField

class formularioFiltroVoo(Form):
    companhia = CharField(max_length=50, required=False, label="Companhia aérea")
    horario_partida = DateTimeField(required=False, widget=DateTimeInput(attrs={'type': 'datetime-local'}), label="Data e horário da partida")
    horario_chegada = DateTimeField(required=False, widget=DateTimeInput(attrs={'type': 'datetime-local'}), label="Data e horário da chegada")
    rota = CharField(max_length=50, required=False)
    chegada = BooleanField(label="O destino é este aeroporto?", required=False)

class formularioCadastroVoo(Form):
    companhia = CharField(max_length=50, required=True, error_messages={'required': 'O nome da companhia aérea é obrigatório'}, label="Companhia aérea")
    horario_partida = DateTimeField(required=True, widget=DateTimeInput(attrs={'type': 'datetime-local'}), error_messages={'required': 'A data de partida é obrigatória'}, label="Data e horário da partida")
    horario_chegada = DateTimeField(required=True, widget=DateTimeInput(attrs={'type': 'datetime-local'}), error_messages={'required': 'A data de chegada é obrigatório'}, label="Data e horário da chegada")
    rota = CharField(max_length=50, required=True, error_messages={'required': 'O nome da rota (ou seja, aeroporto de origem/destino) é obrigatório'}, label="Aeroporto de origem/destino")
    chegada = BooleanField(label="O destino é este aeroporto?", required=False)
class FormularioFiltroRelatorio(Form):
    timestamp_min = DateTimeField(label="O voo terminou depois de:", required=False)
    timestamp_max = DateTimeField(label="O voo terminou antes de:", required=False)
