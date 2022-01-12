# Generated by Django 3.2.6 on 2022-01-11 19:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_alter_comments_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_comment', models.TextField(blank=True, null=True, verbose_name='Комментарий к заказу')),
                ('user', models.CharField(blank=True, max_length=255, null=True, verbose_name='Пользователь')),
                ('first_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Фамилия')),
                ('email', models.EmailField(max_length=254)),
                ('city', models.CharField(blank=True, max_length=255, null=True, verbose_name='Город')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Адрес')),
                ('paid', models.BooleanField(default=False, verbose_name='оплата')),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Доступное количество'),
        ),
        migrations.CreateModel(
            name='ItemsOrdered',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Количество')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='shop.order', verbose_name='Заказ')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.product', verbose_name='Товар')),
            ],
        ),
    ]
