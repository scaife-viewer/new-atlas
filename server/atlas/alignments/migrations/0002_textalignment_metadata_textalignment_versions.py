# Generated by Django 5.1.1 on 2024-10-18 23:00

import sortedm2m.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alignments', '0001_initial'),
        ('texts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='textalignment',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='textalignment',
            name='versions',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, related_name='text_alignments', to='texts.node'),
        ),
    ]
