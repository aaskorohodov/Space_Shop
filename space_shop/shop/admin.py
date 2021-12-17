from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class ValueInline(admin.TabularInline):
    model = PropValue


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    fields = ('title', 'slug', 'content', 'price', 'cat', 'values_get')
    readonly_fields = ('values_get',)

    def values_get(self, product):
        values = PropValue.objects.filter(product=product.pk)
        # for el in values:
        #     print(el.prop.name)
        print(values[0].prop.name)
        # print(values[0].product_id)
        return mark_safe(f"<p> {values[0].prop.name} : {values[0].value} </p><p>Еще характеристики</p>")


class PropertyAdmin(admin.ModelAdmin):
    inlines = [ValueInline,]


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Product, ProductAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductPhoto)