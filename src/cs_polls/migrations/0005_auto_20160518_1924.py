# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-18 22:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cs_polls', '0004_auto_20160518_1922'),
    ]

    operations = [
        migrations.RenameField(
            model_name='poll',
            old_name='can_update',
            new_name='update_allowed',
        ),
    ]
