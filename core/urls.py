from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),

    path('stock/', views.stock_list, name='stock_list'),
    path('stock/add/', views.add_product, name='add_product'),
    path('stock/<int:pk>/toggle/', views.mark_stock_sold, name='mark_stock_sold'),

    path('bill/new/', views.create_invoice, name='create_invoice'),
    path('bill/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('bill/<int:pk>/pay/', views.add_payment, name='add_payment'),
    
    path('expense/add/', views.add_expense, name='add_expense'),
]