from django.shortcuts import render, redirect
from .models import Category, Product, Review, Favourite, Mail, Customer, Order, OrderProduct, ShippingAddress
from django.views.generic import ListView, DetailView
from .forms import LoginForm, RegistrationForm, ReviewForm, ShippingForm, CustomerForm
from django.contrib import messages
from django.contrib.auth import logout, login
from .utils import CartForAuthenticatedUser, get_cart_data
from django.urls import reverse
from django.core.mail import send_mail
from shop import settings
import stripe


# Create your views here.

class ProductList(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'categories'  # objects
    extra_context = {'title': 'Главная страница'}

    def get_queryset(self):
        categories = Category.objects.all()
        data = []
        for category in categories:
            products = category.products.all()
            # products = Product.objects.filter(category=category)
            data.append({
                'title': category.title,
                'products': products[:4]
            })
        return data


class ProductListByCategory(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/category_detail.html'
    paginate_by = 8

    def get_queryset(self):
        sort_field = self.request.GET.get('sort')
        category = Category.objects.get(slug=self.kwargs['slug'])
        products = category.products.all()
        if sort_field:
            products = products.order_by(sort_field)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'Категория: {category.title}'
        return context


class ProductDetail(DetailView):  # product_detail.html
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'Товар: {product.title}'
        products = Product.objects.all()
        data = []
        while len(data) < 4:
            print(len(data))
            from random import randint
            random_index = randint(0, len(products) - 1)
            p = products[random_index]
            if p not in data:
                data.append(p)
        context['products'] = data
        context['reviews'] = Review.objects.filter(product=product)
        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm()
        return context


def login_register(request):
    context = {
        'login_form': LoginForm(),
        'register_form': RegistrationForm(),
        'title': 'Войти или зарегестрироваться'
    }
    return render(request, 'store/login_register.html', context)


def user_login(request):
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('product_list')
    else:
        messages.error(request, 'Не верное имя пользователя или пароль')
        return redirect('login_register')

def user_logout(request):
    logout(request)
    return redirect('product_list')


def register(request):
    form = RegistrationForm(data=request.POST)
    if form.is_valid():
        user = form.save()
        messages.success(request, 'Аккаунт успешно создан. Войдите в аккаунт')
    else:
        for error in form.errors:
            messages.error(request, form.errors[error].as_text())
    return redirect('login_register')


def save_review(request, product_slug):
    form = ReviewForm(data=request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.product = Product.objects.get(slug=product_slug)
        review.save()
    return redirect('product', product_slug)


def save_or_delete_favourite(request, product__slug):
    user = request.user if request.user.is_authenticated else None
    product = Product.objects.get(slug=product__slug)
    if user:
        user_products = Favourite.objects.filter(user=user)
        if product in [i.product for i in user_products]:
            fav_product = Favourite.objects.get(user=user, product=product)
            fav_product.delete()
        else:
            Favourite.objects.create(user=user, product=product)
    next_page = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(next_page)


class FavouriteView(ListView):
    model = Favourite
    context_object_name = 'products'
    template_name = 'store/favourite_products.html'

    def get_queryset(self):
        user = self.request.user
        favs = Favourite.objects.filter(user=user)
        products = [i.product for i in favs]
        return products


def save_mail(request):
    email = request.POST.get('email')
    user = request.user if request.user.is_authenticated else None
    if email:
        Mail.objects.create(mail=email, user=user)
    next_page = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(next_page)


def send_mail_to_all(request):
    from shop import settings
    if request.method == 'POST':
        text = request.POST.get('text')
        mail_list = Mail.objects.all()

        for email in mail_list:
            mail = send_mail(
                subject='У нас новая акция',
                message=text,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False
            )
            print(f'Отправлено ли сообщение на почту {email}? - {bool(mail)}')
    else:
        pass
    return render(request, 'store/send_mail.html')


def cart(request):
    cart_info = get_cart_data(request)
    context = {
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'order': cart_info['order'],
        'products': cart_info['products']
    }
    return render(request, 'store/cart.html', context)


def to_cart(request, product_id, action):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request, product_id, action)
    return redirect('cart')


def clear_cart(request):
    user_cart = CartForAuthenticatedUser(request)
    user_cart.clear()
    messages.success(request, 'Корзина очищена')
    return redirect('cart')

def checkout(request):
    cart_info = get_cart_data(request)
    context = {
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'order': cart_info['order'],
        'items': cart_info['products'],
        'customer_form': CustomerForm(),
        'shipping_form': ShippingForm(),
        'title': 'Оформление заказа'
    }
    return render(request, 'store/checkout.html', context)

# stripe
def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()

        shipping_form = ShippingForm(data=request.POST)
        if shipping_form.is_valid():
            address = shipping_form.save(commit=False)
            address.customer = Customer.objects.get(user=request.user)
            address.order = cart_info['order']
            address.save()

        total_price = cart_info['cart_total_price']
        total_quantity = cart_info['cart_total_quantity']

        session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Товары с TOTEMBO'
                        },
                        'unit_amount': int(total_price * 100)
                    },
                    'quantity': total_quantity
                }
            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )
        return redirect(session.url, 303)


def success_payment(request):
    user_cart = CartForAuthenticatedUser(request)
    user_cart.clear()
    return render(request, 'store/success.html')


# Сделать отображение в админте Заказов и адресов доставки
