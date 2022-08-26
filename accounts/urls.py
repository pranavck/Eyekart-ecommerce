from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.signout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),



    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('forgotPassword/',views.forgotPassword,name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/',views.resetPassword,name='resetPassword'),

    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/',views.edit_profile, name='edit_profile'),
    path('change_passworod/',views.change_password, name='change_password'),
    path('order_detail/<order_id>/',views.order_detail, name='order_detail'),
    path('cancel_order/<payment_id>/', views.cancel_order, name='cancel_order'),



]
