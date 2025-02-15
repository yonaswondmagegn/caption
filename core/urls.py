from django.urls import path
from .views import CreateCaptionView

urlpatterns = [
    path('yt',CreateCaptionView.as_view())
]