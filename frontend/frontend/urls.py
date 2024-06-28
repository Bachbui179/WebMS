from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('products/', views.product_view, name='products'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'frontend.views.error_404'