# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-05 17:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reg_log', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='CSV_list',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Depertment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='DeptOrg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('college', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reg_log.college')),
                ('dept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TRAINING.Depertment')),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reg_log.organiser')),
            ],
        ),
        migrations.CreateModel(
            name='Foss',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TRAINING.Category')),
            ],
        ),
        migrations.CreateModel(
            name='MasterBatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('college', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reg_log.college')),
            ],
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('csv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TRAINING.CSV_list')),
                ('depertment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TRAINING.Depertment')),
                ('foss', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TRAINING.Foss')),
                ('organiser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reg_log.organiser')),
            ],
        ),
        migrations.AddField(
            model_name='csv_list',
            name='masterbatch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TRAINING.MasterBatch'),
        ),
    ]
