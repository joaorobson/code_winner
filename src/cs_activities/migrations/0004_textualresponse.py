# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-07 02:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cs_activities', '0003_auto_20160307_0239'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextualResponse',
            fields=[
                ('response_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cs_activities.Response')),
                ('text', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('cs_activities.response',),
        ),
    ]
