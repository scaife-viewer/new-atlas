# Generated by Django 5.1.1 on 2024-10-15 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('idx', models.IntegerField(blank=True, help_text='0-based index', null=True)),
                ('kind', models.CharField(max_length=255)),
                ('urn', models.CharField(max_length=255, unique=True)),
                ('ref', models.CharField(blank=True, max_length=255, null=True)),
                ('rank', models.IntegerField(blank=True, null=True)),
                ('text_content', models.TextField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
