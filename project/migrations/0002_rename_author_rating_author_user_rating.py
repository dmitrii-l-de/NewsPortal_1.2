# Generated by Django 4.1.2 on 2022-10-04 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='author',
            old_name='author_rating',
            new_name='user_rating',
        ),
    ]
