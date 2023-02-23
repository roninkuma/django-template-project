from django.contrib import admin
from .models import Category, Product, Gallery, Review, Favourite, Mail, Order, OrderProduct, Customer, ShippingAddress
from django.utils.safestring import mark_safe
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'get_product_count']
    prepopulated_fields = {'slug': ('title',)}


    def get_product_count(self, obj):
        if obj.products:
            return str(len(obj.products.all()))
        else:
            return '0'

    get_product_count.short_description = 'Кол-во товаров'


class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1


class ReviewInline(admin.TabularInline):
    model = Review
    fk_name = 'product'
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category',
                    'price', 'quantity', 'size', 'color',
                    'get_count_reviews', 'get_photo']
    list_editable = ['price', 'quantity', 'size', 'color']
    inlines = [GalleryInline, ReviewInline]
    prepopulated_fields = {'slug': ('title', )}
    list_display_links = ['title']


    def get_photo(self, obj):
        if obj.photos:
            try:
                return mark_safe(f'<img src="{obj.photos.first().image.url}" width="75">')
            except:
                return '-'
        else:
            return '-'

    get_photo.short_description = 'Миниатюра'

    def get_count_reviews(self, obj):
        if obj.review_set:
            try:
                return str(len(obj.review_set.all()))
            except:
                return '0'
        else:
            return '0'

    get_count_reviews.short_description = 'Отзывы'



class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'created_at']
    list_display_links = ['id']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Favourite)
admin.site.register(Mail)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Customer)
admin.site.register(ShippingAddress)
