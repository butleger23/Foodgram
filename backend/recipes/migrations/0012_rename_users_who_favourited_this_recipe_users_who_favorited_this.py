# Generated by Django 5.1.6 on 2025-02-23 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_recipe_short_link'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='users_who_favourited_this',
            new_name='users_who_favorited_this',
        ),
    ]
