from django.urls import path
from . import views

urlpatterns = [
    path('place_older/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('payment_midtrants/', views.payment_midtrants, name='payment'),
    path('payment_proses/', views.payment_proses, name='payment_proses'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('midtrants_callback/', views.midtrants_callback, name='midtrants_callback'),
    path('batal_order/<int:order_id>/', views.batal_order, name='batal_order'),

    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),

    path('my_orders/', views.my_orders, name='my_orders'),
    path('my_orders/pending/', views.status_pending, name='pending'),
    path('my_orders/on_the_way/', views.status_on_the_way, name='on_the_way'),
    path('my_orders/delivered/', views.status_delivered, name='delivered'),
    path('my_orders/cencelled/', views.status_cencelled, name='cencelled'),
    path('my_orders/all_order/', views.all_order, name='all_order'),
    
    path('order_accept/<int:order_id>/', views.order_accept, name='order_accept'),
    

    path('my_transaction/', views.my_transaction, name='my_transaction'),
    path('my_transaction/<str:number>/', views.transaction_detail, name='my_transaction_detail'),
    
    path('get_review/<int:order_id>/', views.get_review, name='get_review'),
    path('get_review/submit_review/<int:item_id>/', views.submit_review, name='submit_review'),
]