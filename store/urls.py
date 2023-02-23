from django.urls import path
from .views import *

urlpatterns = [
    path('', ProductList.as_view(), name='product_list'),
    path('category/<slug:slug>/', ProductListByCategory.as_view(), name='category'),
    path('product/<slug:slug>/', ProductDetail.as_view(), name='product'),
    path('login_register/', login_register, name='login_register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),
    path('save_review/<slug:product_slug>', save_review, name='save_review'),
    path('add_or_delete_fav/<slug:product__slug>', save_or_delete_favourite, name='save_or_delete_fav'),
    path('favourite', FavouriteView.as_view(), name='favourite'),
    path('save_mail', save_mail, name='save_mail'),
    path('send_mail', send_mail_to_all),
    path('cart', cart, name='cart'),
    path('to_cart/<int:product_id>/<str:action>/', to_cart, name='to_cart'),
    path('clear_cart', clear_cart, name='clear'),
    path('checkout', checkout, name='checkout'),
    path('payment', create_checkout_session, name='payment'),
    path('success', success_payment, name='success')
]