from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from rest_framework import status
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password,make_password


class GoogleAuth(APIView):
    def post(self, request):
        try:
            access_token = request.data.get('token')
            if not access_token:
                return Response({'error': "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Verify the access token with Google
            google_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}

            response = requests.get(google_url, headers=headers)

            if response.status_code != 200:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

            user_data = response.json()
            email = user_data.get('email')
            google_uid = user_data.get('sub')

            if not email:
                return Response({'error': "Invalid token data"}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create user
            user, created = User.objects.get_or_create(
                email=email, defaults={'username': email})
            if created:
                SocialAccount.objects.create(
                    user=user, provider='google', uid=google_uid)

            refresh = RefreshToken.for_user(user)
            return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})
        except:
            return Response({"error":"something wrong happend try again"},status=status.HTTP_400_BAD_REQUEST)

class EmailAccepter(APIView):
    def post(self,request):
        email = request.data.get('email')
        if not email:
            return Response({'email':'email is requred'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.filter(email = email).first()
            if user:
                social_user = SocialAccount.objects.filter(user = user).first()
                if social_user:
                    return Response({
                        "email":email,
                        "social":True,
                        "condition":'R'
                    },status=status.HTTP_200_OK)
                return Response({
                    "email":email,
                    "social":False,
                    "condition":'R'
                },status=status.HTTP_200_OK)
            else:
                return Response({
                    "email":email,
                    "social":False,
                    "condition":"NR",
                },status=status.HTTP_200_OK)
        except:
            return Response({'error':'something went wrong try again !'},status=status.HTTP_400_BAD_REQUEST)
        

class LoginUser(APIView):
    def post(slef,request):
        try:

            data = request.data
            email = data.get('email')
            password = data.get('password')

            if not email:
                return Response({'error':'email is requred'},status=status.HTTP_400_BAD_REQUEST)
            if not password:
                return Response({'error':'password is requred'},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(email = email)
            except:
                return Response({'error':'user not found'},status=status.HTTP_404_NOT_FOUND)
            
            is_password_valid = check_password(password,user.password)

            if not is_password_valid:
                return Response({'error','wrong passowrd'},status=status.HTTP_400_BAD_REQUEST)
            
            refresh = RefreshToken.for_user(user)
            return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})
        except:
            return Response({'error':'something went wrong try again '},status=status.HTTP_400_BAD_REQUEST)



class RegisterUser(APIView):
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')
            password = data.get('password')

            if not email:
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not password:
                return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email).exists():
                return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create(
                username=email,
                email=email,
                password=make_password(password)  
            )

            refresh = RefreshToken.for_user(user)
            return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})

        except Exception as e:
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)