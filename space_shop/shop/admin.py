from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class ValueInline(admin.TabularInline):
    model = PropValue


class ProductPhotoInLine(admin.TabularInline):
    model = ProductPhoto

    # def get_queryset(self, request):
    #     print(request)


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    fields = ('title', 'slug', 'content', 'price', 'currency', 'cat', 'primary_photo', 'quantity')
    inlines = [ProductPhotoInLine, ValueInline]


class PropertyAdmin(admin.ModelAdmin):
    inlines = [ValueInline,]


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Product, ProductAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductPhoto)
admin.site.register(Comments)
admin.site.register(PropValue)
admin.site.register(Order)