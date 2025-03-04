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
