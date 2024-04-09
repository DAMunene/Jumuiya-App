from django.urls import path 
from .import views

urlpatterns = [
    path('', views.store, name = 'store'),
    path('cart/', views.cart, name = 'cart'),
    path('checkout/', views.checkout, name = 'checkout'),

     path('update_item/', views.updateItem, name = 'update-item'),
     path('process_order/', views.processOrder, name = 'process-order'),
     path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
     path('<str:ref>/', views.verify_payment, name='verify-payment'),
]