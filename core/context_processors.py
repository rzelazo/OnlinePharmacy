from .models import *


def categories_context(request):
    categories = [Category.objects.get(name="Zdrowie"),
                  Category.objects.get(name="Higiena"),
                  Category.objects.get(name="Pielęgnacja")]
    return {"categories": categories}
