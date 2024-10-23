from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_admin, name='dashboard_admin'),
    # URL ORDER
    path('orders/', views.orders, name='orders'),
    path('orders-peding/', views.orders_pending, name='orders_pending'),
    path('orders-confirm/', views.orders_confirm, name='orders_confirm'),
    path('orders-on_the_way/', views.orders_otw, name='orders_on_the_way'),
    path('orders-delivered/', views.orders_delivered, name='orders_delivered'),
    path('orders-batal/', views.orders_batal, name='orders_batal'),
    #URL ORDER ACTIONS
    path('order/<int:order_id>/', views.orderDetail, name='order_detail_admin'),
    # path('batal_order/<int:order_id>/', views.batal_order, name='batal_order'),
    path('confirm_order/<int:order_id>/', views.confirm_order, name='confirm_order'),
    path('ready_to_sent/<int:order_id>/', views.ready_to_sent, name='ready_to_sent'),

    # URL CATEGORY
    path('category/', views.category, name='category'),
    path('add_category/', views.add_category, name='add_category'),
    path('edit-category/<slug>/<uuid:pk>/', views.edit_category, name='edit_category'),
    path('delete-category/<slug>/<uuid:pk>/', views.delete_category, name='delete_category'),

    # URL PRODUCT
    path('products/', views.products, name='products'),
    path('add-product/', views.set_product, name='add_product'),
    path('edit-product/<uuid:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<uuid:pk>/', views.delete_product, name='delete_product'),

    path('add-product/api/product-attribute-options-color/', views.get_product_attribute_value_color, name='get_product_attribute_value_color'),
    path('add-product/api/create-product-attribute-color/', views.post_create_product_attribute_color, name='post-create-product-attribute-color'),

    path('add-product/api/product-attribute-options-size/', views.get_product_attribute_value_size, name='get_product_attribute_value_size'),

    # URL PRODUCT WAREHOUSE
    #path('warehouse/', views.warehouse, name='warehouse'),
    path('add-warehouse/', views.add_warehouse, name='add_warehouse'),
    #path('edit-warehouse/<uuid:pk>/', views.edit_warehouse, name='edit_warehouse'),
    #path('delete-warehouse/<uuid:pk>/', views.delete_warehouse, name='delete_warehouse'),

    
    # URL Analytics
    path('payment_analisis/', views.payment_analisis, name='payment_analisis'),
    path('analisis/', views.analisis, name='analisis'),

    path('customers/', views.customers, name='customers'),
    
    path('profile/', views.profile, name='profile'),
    

]