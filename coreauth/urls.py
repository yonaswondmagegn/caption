from django.urls import path
from .views import GoogleAuth,EmailAccepter,LoginUser,RegisterUser


urlpatterns = [
    path('verify/',GoogleAuth.as_view()),
    path('accept/',EmailAccepter.as_view()),
    path('login/',LoginUser.as_view()),
    path('register/',RegisterUser.as_view()),
]