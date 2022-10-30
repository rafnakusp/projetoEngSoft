# Generated by Django 4.1.2 on 2022-10-08 20:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0002_delete_progressovoo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgressoVoo',
            fields=[
                ('progresso_id', models.IntegerField(primary_key=True, serialize=False)),
                ('horario_partida_real', models.DateTimeField(null=True)),
                ('horario_chegada_real', models.DateTimeField(null=True)),
                ('status_voo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book.status')),
                ('voo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book.voo')),
            ],
            options={
                'db_table': 'progressoVoo',
            },
        ),
    ]