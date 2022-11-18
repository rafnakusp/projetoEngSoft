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
    intervalo_previsto = IntervaloDatasField(required=False, widget=IntervaloDatas(\
        widgets=[DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData), \
        DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData)]), \
        label="Intervalo de busca da data e horário previstos")
    rota = CharField(max_length=50, required=False, error_messages={'required': 'O nome da rota (ou seja, aeroporto de origem/destino) é obrigatório'}, label="Aeroporto de origem/destino")
    chegada = BooleanField(label="O destino é este aeroporto?", required=False)

class formularioCadastroVoo(Form):
    companhia = CharField(max_length=50, required=True, error_messages={'required': 'O nome da companhia aérea é obrigatório'}, label="Companhia aérea")
    horario_previsto = DateTimeField(required=True, widget=DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData), error_messages={'required': 'A data é obrigatória'}, label="Data e horário previsto")
    rota = CharField(max_length=50, required=True, error_messages={'required': 'O nome da rota (ou seja, aeroporto de origem/destino) é obrigatório'}, label="Aeroporto de origem/destino")
    chegada = BooleanField(label="O destino é este aeroporto?", required=False)

class FormularioFiltroRelatorioVoosRealizados(Form):
    companhia = CharField(max_length=50, required=False, label="Companhia aérea:")
    intervalo_real = IntervaloDatasField(required=False, widget=IntervaloDatas(\
        widgets=[DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData), \
        DateTimeInput(attrs={'type': 'datetime-local'}, format=formatoData)]), \
        label="Intervalo de busca da data e horário real")

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
    opcoes_atraso = [
        ('', ''),
        ('1-10min', 'até 10 minutos'),
        ('10min-1h', 'entre 10 minutos e 1 hora'),
        ('1-3h', 'entre 1 e 3 horas'),
        ('>3h', 'mais de 3 horas')
    ]
    companhia = CharField(max_length=50, required=False, label="Companhia aérea:")
    status = ChoiceField(choices=opcoes_status, required=False, label="Status dos voos")
    atraso = ChoiceField(choices=opcoes_atraso, required=False, label="Atraso do voo")

