# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-09 08:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TRAINING', '0003_auto_20170608_1045'),
    ]

    operations = [
        migrations.AddField(
            model_name='foss',
            name='with_exam',
            field=models.BooleanField(default=True),
        ),
    ]
