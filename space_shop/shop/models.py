from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name='Текст описания')
    price = models.DecimalField(max_digits=30, decimal_places=5, verbose_name='Цена')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, blank=True, null=True, verbose_name='Категории')


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Категория')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")


class Property(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Характеристика')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, blank=True, null=True, verbose_name='Категория')


class PropValue(models.Model):
    value = models.CharField(max_length=255, unique=True, verbose_name='Значение')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, null=True, verbose_name='Товар')
    prop = models.ForeignKey('Property', on_delete=models.PROTECT, null=True, verbose_name='Характеристика')