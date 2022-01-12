from django.db import models
from django.urls import reverse


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name='Текст описания')
    price = models.DecimalField(max_digits=30, decimal_places=0, verbose_name='Цена')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, blank=True, null=True, verbose_name='Категории')
    primary_photo = models.ImageField(upload_to="photos/PrymaryPhoto", blank=True, null=True, verbose_name='Фото')
    currency = models.CharField(max_length=255, blank=True, null=True, verbose_name='Валюта')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Доступное количество')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product', kwargs={'post_slug': self.slug, 'cat_slug': self.cat.slug})


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Категория')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    short_description = models.TextField(blank=True, verbose_name='Короткое описание категории')
    full_description = models.TextField(blank=True, verbose_name='Полное описание категории')
    cat_image = models.ImageField(upload_to="cat_photos", null=True, verbose_name='Картинка категории')

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
    value = models.CharField(max_length=255, unique=False, verbose_name='Значение')
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, verbose_name='Товар')
    prop = models.ForeignKey('Property', on_delete=models.PROTECT, null=True, verbose_name='Характеристика')

    def __str__(self):
        return self.value


class ProductPhoto(models.Model):
    photo = models.ImageField(upload_to="photos", verbose_name='Фото')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Товар')

    def __str__(self):
        return self.product.title


class Comments(models.Model):
    text = models.TextField(verbose_name='Комментарий')
    user = models.CharField(max_length=255, unique=False, null=True, blank=True, verbose_name='Пользователь')
    rating = models.CharField(max_length=255, null=True, blank=True, verbose_name='Оценка')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, null=True, verbose_name='Товар')


class Order(models.Model):
    order_comment = models.TextField(unique=False, null=True, blank=True, verbose_name='Комментарий к заказу')
    user = models.CharField(max_length=255, unique=False, null=True, blank=True, verbose_name='Пользователь')
    first_name = models.CharField(max_length=255, unique=False, null=True, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=255, unique=False, null=True, blank=True, verbose_name='Фамилия')
    email = models.EmailField()
    city = models.CharField(max_length=255, unique=False, null=True, blank=True, verbose_name='Город')
    address = models.CharField(max_length=255, unique=False, null=True, blank=True, verbose_name='Адрес')
    paid = models.BooleanField(default=False, verbose_name='оплата')


class ItemsOrdered(models.Model):
    order = models.ForeignKey('Order', on_delete=models.PROTECT, null=True, blank=True, verbose_name='Заказ')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')