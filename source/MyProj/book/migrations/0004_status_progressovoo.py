# Generated by Django 4.1.1 on 2022-10-07 20:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0003_voo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('status_id', models.IntegerField(primary_key=True, serialize=False)),
                ('status_nome', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'status',
            },
        ),
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
