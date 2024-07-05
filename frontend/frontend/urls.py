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
    path('order/', views.view_order, name='view_order'),
    path('order/add/<int:item_id>/', views.add_order_item, name='add_order_item'),
    path('order/remove/<int:item_id>/', views.remove_order_item, name='remove_order_item'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'frontend.views.error_404'