# Generated by Django 3.2.6 on 2022-01-06 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_auto_20211228_1652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='full_description',
            field=models.TextField(blank=True, verbose_name='Полное описание категории'),
        ),
        migrations.AlterField(
            model_name='comments',
            name='user',
            field=models.CharField(max_length=255, verbose_name='Пользователь'),
        ),
    ]
