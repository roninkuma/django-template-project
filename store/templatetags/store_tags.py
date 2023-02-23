from django import template
from store.models import Category, Favourite

register = template.Library()

@register.simple_tag()
def get_categories():
    return Category.objects.all()


@register.simple_tag()
def get_sorted():
    sorters = [
        {
            'title': 'По цене',
            'sorters': [
                ['price', 'По возрастанию'],
                ['-price', 'По убыванию']
            ]
        },
        {
            'title': 'По цвету/материалу',
            'sorters': [
                ['color', 'От А до Я'],
                ['-color', 'От Я до А']
            ]
        },
        {
            'title': 'По размеру',
            'sorters': [
                ['size', 'По возрастанию'],
                ['-size', 'По убыванию']
            ]
        },
        {
            'title': 'По названию',
            'sorters': [
                ['title', 'От А до Я'],
                ['-title', 'От Я до А']
            ]
        }

    ]

    return sorters


@register.simple_tag()
def get_favourite(user):
    favs = Favourite.objects.filter(user=user)
    products = [i.product for i in favs]
    return products

