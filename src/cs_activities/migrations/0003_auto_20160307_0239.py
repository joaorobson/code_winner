# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-07 02:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cs_activities', '0002_auto_20160307_0208'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CodingActivity',
        ),
        migrations.DeleteModel(
            name='QuestionActivity',
        ),
    ]
