# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-08 10:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reg_log', '0001_initial'),
        ('TRAINING', '0002_auto_20170605_1830'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('csv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TRAINING.CSV_list')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reg_log.college')),
            ],
        ),
        migrations.AddField(
            model_name='foss',
            name='available_for_training',
            field=models.BooleanField(default=True),
        ),
    ]
