# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-09 00:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reg_log', '0004_auto_20170706_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='organiserhandover',
            name='status',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]