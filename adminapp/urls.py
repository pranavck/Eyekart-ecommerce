from django.urls import path
from . import views

urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_management', views.user_management, name='user_management'),
    path('delete_user/<user_id>', views.delete_user, name='delete_user'),
    path('product_management', views.product_management, name='product_management'),
    path('category_management', views.category_management, name='category_management'),
    path('admin_login', views.admin_login, name='admin_login'),
    path('admin_logout', views.admin_logout, name='admin_logout'),
    path('add_product', views.add_product, name='add_product'),
]
