from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name='Наименование категории')
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='Изображение')
    slug = models.SlugField(unique=True)

    def get_category_photo(self):
        if self.image:
            return self.image.url
        else:
            return 'https://studenthack.uz/wp-content/uploads/2021/11/%D0%A4%D0%BE%D1%82%D0%BE-%D1%81%D0%BA%D0%BE%D1%80%D0%BE-%D0%B1%D1%83%D0%B4%D0%B5%D1%82.png'


    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'категории'


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.IntegerField(default=0, verbose_name='Кол-во на складе')
    description = models.TextField(default='Здесь будет описание', verbose_name='Описание')
    size = models.IntegerField(default=30, verbose_name='Размер в мм')
    color = models.CharField(max_length=30, default='Серебро', verbose_name='Цвет/материал')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 verbose_name='Категория', related_name='products')
    slug = models.SlugField(unique=True, null=True)

    def get_absolute_url(self):
        return reverse('product', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    def get_first_photo(self):
        if self.photos:
            try:
                return self.photos.first().image.url
            except:
                return 'https://studenthack.uz/wp-content/uploads/2021/11/%D0%A4%D0%BE%D1%82%D0%BE-%D1%81%D0%BA%D0%BE%D1%80%D0%BE-%D0%B1%D1%83%D0%B4%D0%B5%D1%82.png'
        else:
            return 'https://studenthack.uz/wp-content/uploads/2021/11/%D0%A4%D0%BE%D1%82%D0%BE-%D1%81%D0%BA%D0%BE%D1%80%D0%BE-%D0%B1%D1%83%D0%B4%D0%B5%D1%82.png'


    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='products', verbose_name='Изображение')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Галлерея товаров'


class Review(models.Model):
    text = models.TextField(verbose_name='Текст отзыва')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')

    def __str__(self):
        return f'{self.user.username} - {self.product.title}'

    class Meta:
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Таблица избранных товаров'



class Mail(models.Model):
    mail = models.EmailField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.mail

    class Meta:
        verbose_name = 'Почта'
        verbose_name_plural = 'Таблица почтовых адресов'


class Customer(models.Model):
    user = models.OneToOneField(User, models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(verbose_name='Почта')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    @property
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_total_price for product in order_products])
        return total_price

    @property
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([product.quantity for product in order_products])
        return total_quantity

    def __str__(self):
        return self.customer.name

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказах'


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Таблица адресов доставки'

