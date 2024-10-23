from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('', views.dashboard, name='dashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),

    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    
    path('address/', views.address, name='address'),
    path('address/add-address/', views.add_address, name="add_address"),
    path('address/edit/<slug:id>/', views.edit_address, name='edit_address'),
    path('address/delete/<slug:id>/', views.delete_address, name='delete_address'),
    path('address/set_default/<slug:id>/', views.set_default, name='set_default'),
    
    path('city/', views.getCity, name="city"),
    path('district/', views.getDistrict, name="district"),

    #wistlist
    path('my_wishlists/', views.my_wishlists, name='my_wishlists'),
    path('wistlist/add_to_wislist/<uuid:id>', views.add_to_wislist, name='user_wislist'),
]