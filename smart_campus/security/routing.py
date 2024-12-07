from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/security/$', consumers.SecurityConsumer.as_asgi()),
    re_path(r'ws/cameras/(?P<camera_id>\w+)/$', consumers.CameraConsumer.as_asgi()),
]
