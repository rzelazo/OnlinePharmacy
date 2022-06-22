from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

app_name = 'core'

urlpatterns = [
    path('', views.ItemListView.as_view(), name="index"),
    path('<int:pk>/detail/', views.ItemDetailView.as_view(), name="detail"),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/remove/<int:pk>/', views.RemoveFromCartView.as_view(), name='cart-remove'),
    path('checkout/', views.CheckoutView.as_view(template_name='core/checkout.html'), name='checkout'),
    path('category/<int:pk>/', views.CategoryFilteredView.as_view(), name='category-filtered'),
    path('user/', views.UserView.as_view(), name='user'),
    path('checkout/summary/', TemplateView.as_view(template_name="core/summary.html"), name="summary")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
