import datetime
from typing import Any, Optional, Sequence, Type, Union
from django.forms.utils import from_current_timezone
from django.utils.dateparse import parse_datetime
from django.forms import DateTimeField, DateTimeInput, CharField, Form, BooleanField, MultiWidget, ValidationError, ChoiceField, Widget

formatoData = "%Y-%m-%dT%H:%M"

class IntervaloDatasField(DateTimeField):
        # def __init__(self, input_formats: Optional[Any] = ..., required: bool = ..., widget: Optional[Union[Widget, Type[Widget]]] = ..., label: Optional[Any] = ..., initial: Optional[Any] = ..., help_text: str = ..., error_messages: Optional[Any] = ..., show_hidden_initial: bool = ..., validators: Sequence[Any] = ..., localize: bool = ..., disabled: bool = ..., label_suffix: Optional[Any] = ...) -> None:
        #     self.empty_values.append([None, None])
        #     super().__init__()
        def to_python(self, value):
            """
            Validate that the input can be converted to a datetime. Return a
            Python datetime.datetime object.
            """
            print(value)
            print(self.empty_values)
            if value in self.empty_values:
                return None
            end = []
            for v in value:
                if v in self.empty_values:
                    end.append(None)
                if isinstance(v, datetime.datetime):
                    end.append(from_current_timezone(v))
                elif isinstance(value[0], datetime.date):
                    result = datetime.datetime(v.year, v.month, v.day)
                    end.append(from_current_timezone(result))
                else:
                    try:
                        result = parse_datetime(v.strip())
                    except ValueError:
                        raise ValidationError(self.error_messages["invalid"], code="invalid")
                if not result:
                    result = super().to_python(v)
                end.append(from_current_timezone(result))
            return end

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
    status = ChoiceField(choices=opcoes_status, required=False)

