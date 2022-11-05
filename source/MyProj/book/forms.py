from datetime import datetime
from django.forms import DateTimeField, DateTimeInput, CharField, Form, BooleanField, MultiWidget, MultipleChoiceField, ValidationError, ChoiceField, Widget

formatoData = "%Y-%m-%dT%H:%M"

class IntervaloDatasField(MultipleChoiceField):
    def valid_value(self, value):
        """Check to see if the provided value is a valid choice."""
        if type(value) == datetime or value == '':
            return True
        elif value == None or value == 'None':
            return False
        elif type(value) == str:
            try:
                datetime.strptime(value, "%Y-%m-%dT%H:%M")
                return True
            except:
                return False
        return False

class IntervaloDatas(MultiWidget):
        def decompress(self, value):
            if value == None:
                return [None, None]
            elif len(value) == 0:
                return [None, None]
            elif len(value) == 1:
                return [value[0], None]
            return [value[0], value[1]]

class formularioFiltroVoo(Form):
    companhia = CharField(max_length=50, required=False, label="Companhia aérea")
    intervalo_partida = IntervaloDatasField(required=False, widget=IntervaloDatas(\
        widgets=[DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData), \
        DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData)]), \
        label="Intervalo de busca da data e horário da partida")
    intervalo_chegada = IntervaloDatasField(required=False, widget=IntervaloDatas(\
        widgets=[DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData), \
        DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData)]), \
        label="Intervalo de busca da data e horário da chegada")
    rota = CharField(max_length=50, required=False)
    chegada = BooleanField(label="O destino é este aeroporto?", required=False)

class formularioCadastroVoo(Form):
    companhia = CharField(max_length=50, required=True, error_messages={'required': 'O nome da companhia aérea é obrigatório'}, label="Companhia aérea")
    horario_partida = DateTimeField(required=True, widget=DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData), error_messages={'required': 'A data de partida é obrigatória'}, label="Data e horário da partida")
    horario_chegada = DateTimeField(required=True, widget=DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData), error_messages={'required': 'A data de chegada é obrigatório'}, label="Data e horário da chegada")
    rota = CharField(max_length=50, required=True, error_messages={'required': 'O nome da rota (ou seja, aeroporto de origem/destino) é obrigatório'}, label="Aeroporto de origem/destino")
    chegada = BooleanField(label="O destino é este aeroporto?", required=False)

class FormularioFiltroRelatorioVoosRealizados(Form):
    companhia = CharField(max_length=50, required=False, label="Companhia aérea:")
    intervalo_partida = IntervaloDatasField(required=False, widget=IntervaloDatas(\
        widgets=[DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData), \
        DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData)]), \
        label="Intervalo de busca da data e horário da partida")
    intervalo_chegada = IntervaloDatasField(required=False, widget=IntervaloDatas(\
        widgets=[DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData), \
        DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData)]), \
        label="Intervalo de busca da data e horário da chegada")

class FormularioFiltroRelatorioVoosAtrasados(Form):
    opcoes_status = [
        ('', ''),
        ('-', '-'),
        ('Embarque', 'Embarque'),
        ('Programado', 'Programado'),
        ('Taxiando', 'Taxiando'),
        ('Pronto', 'Pronto'),
        ('Autorizado', 'Autorizado'),
        ('Em voo', 'Em voo'),
        ('Aterrissado', 'Aterrissado')
    ]
    companhia = CharField(max_length=50, required=False, label="Companhia aérea:")
    status = ChoiceField(choices=opcoes_status, required=False, label="Status dos voos")

