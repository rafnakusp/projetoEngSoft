# Generated by Django 4.1.2 on 2022-11-11 19:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0010_rename_horario_chegada_previsto_voo_horario_previsto_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='progressovoo',
            old_name='horario_chegada_real',
            new_name='horario_real',
        ),
        migrations.RemoveField(
            model_name='progressovoo',
            name='horario_partida_real',
        ),
    ]