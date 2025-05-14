from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not username or not email or not password:
            return Response({'error': 'Please provide username, email, and password'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'token': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Please provide username and password'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({'error': 'Invalid credentials'}, 
                           status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'token': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_200_OK)

class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get the current user's profile information"""
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email
        })
    
    def put(self, request):
        """Update the current user's profile information"""
        user = request.user
        username = request.data.get('username')
        email = request.data.get('email')
        
        if not username and not email:
            return Response({'error': 'Please provide at least one field to update'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        if username and username != user.username and User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        if email and email != user.email and User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        if username:
            user.username = username
        if email:
            user.email = email
        
        user.save()
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email
        }) 