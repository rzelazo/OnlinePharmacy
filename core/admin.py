from django.contrib import admin
from .models import *


admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Manufacturer)
admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)
