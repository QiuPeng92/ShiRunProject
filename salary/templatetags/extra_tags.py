from django import template
from decimal import Decimal

register = template.Library()


@register.filter(name='multiply')  # 过滤器在模板中使用的名字
def myMultiply(value, arg):
    value = Decimal(value)
    ret = value * Decimal(0.55)
    return round(ret,2)
