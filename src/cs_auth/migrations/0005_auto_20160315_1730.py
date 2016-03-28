# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-15 17:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0007_alter_validators_add_error_messages'),
        ('cs_auth', '0004_auto_20160315_1542'),
    ]

    operations = [
        migrations.CreateModel(
            name='SingleUserGroup',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.Group')),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            bases=('auth.group',),
        ),
        migrations.DeleteModel(
            name='AllowedUserList',
        ),
    ]
