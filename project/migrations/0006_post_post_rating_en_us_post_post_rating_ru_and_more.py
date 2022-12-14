# Generated by Django 4.1.2 on 2022-11-17 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_category_category_name_en_us_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_rating_en_us',
            field=models.IntegerField(db_column='post_rating_en_us', default=0, null=True, verbose_name='Post rating'),
        ),
        migrations.AddField(
            model_name='post',
            name='post_rating_ru',
            field=models.IntegerField(db_column='post_rating_ru', default=0, null=True, verbose_name='Post rating'),
        ),
        migrations.AddField(
            model_name='post',
            name='pub_date_en_us',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Publication date'),
        ),
        migrations.AddField(
            model_name='post',
            name='pub_date_ru',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Publication date'),
        ),
    ]
