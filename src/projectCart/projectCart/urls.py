from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    # path('securelogin/', admin.site.urls),

    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about-us/', views.about, name='about'),
    path('testimonial/', views.testimonial, name='testimonial'),
    
    path('testchat/', views.chat_bubble , name='testchat'),

    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('orders/', include('orders.urls')),

    # authentication
    path('account/', include('profiles.urls')),
    path('accounts/', include('allauth.urls')),
    
    path('blogs/', include('blog.urls')),
    #chat
    path('', include('chat.urls')),
    #admin
    path('app-admin/', include('appadmin.urls')),

    #ckeditor_5
    path('ckeditor5/', include('django_ckeditor_5.urls')),


    path("__debug__/", include("debug_toolbar.urls")),
] 

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
