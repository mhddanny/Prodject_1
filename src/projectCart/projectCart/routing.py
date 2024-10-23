# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application

from django.urls import path
from chat import consumers

# import chat.routing

websocket_urlpatterns = [
    path('ws/<str:uuid>/', consumers.ChatConsumer.as_asgi())
]


# application = ProtocolTypeRouter({
#     'http': get_asgi_application,
#     'websocket': AuthMiddlewareStack(
#         URLRouter(
#             chat.routing.websocket_urlpatterns
#         )
#     ),
# })
