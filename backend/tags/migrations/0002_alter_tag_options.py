# Generated by Django 5.1.6 on 2025-03-01 16:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('slug',), 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
    ]
