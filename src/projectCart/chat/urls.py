from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('api/create-room/<str:uuid>/', views.create_room, name='create-room'),
    path('chat-admin/', views.chatAdmin, name='chat-admin'),
    path('chat-admin/<str:uuid>', views.chatAdminRoom, name='chat-admin-room'),
    path('chat-admin/<str:uuid>/delete', views.deleteAdminRoom, name='delete-admin-room'),

    path('contact-admin/', views.contactUs, name='contact-admin'), 

]