# Generated by Django 3.2.3 on 2025-02-10 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodgramuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='user_avatars', verbose_name='Аватар'),
        ),
    ]
