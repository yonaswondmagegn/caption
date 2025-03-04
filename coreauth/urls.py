from django.urls import path
from .views import GoogleAuth


urlpatterns = [
    path('verify/',GoogleAuth.as_view())
]