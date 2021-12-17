from django.db import models
from django.urls import reverse


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name='Текст описания')
    price = models.DecimalField(max_digits=30, decimal_places=5, verbose_name='Цена')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, blank=True, null=True, verbose_name='Категории')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Категория')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})


class Property(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Характеристика')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, blank=True, null=True, verbose_name='Категория')

    def __str__(self):
        return self.name


class PropValue(models.Model):
    value = models.CharField(max_length=255, unique=True, verbose_name='Значение')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, null=True, verbose_name='Товар')
    prop = models.ForeignKey('Property', on_delete=models.PROTECT, null=True, verbose_name='Характеристика')


class ProductPhoto(models.Model):
    photo = models.ImageField(upload_to="photos", verbose_name='Фото')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, null=True, blank=True, verbose_name='Товар')

    def __str__(self):
        return self.product.title
