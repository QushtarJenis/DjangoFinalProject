from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.urls import resolve
import re

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info.startswith('/admin') or request.path_info.startswith('/static/') or request.path_info == '/favicon.ico':
            return None
        if request.method == 'OPTIONS':
            return None

        if request.path_info == '/':
            return None

        public_paths = [
            '/api/auth/login',
            '/api/auth/register',
            '/api/auth/token/refresh',
        ]

        current_path = request.path_info.rstrip('/') 
        
        if any(current_path == path or current_path.startswith(path + '/') for path in public_paths):
            return None

        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return JsonResponse({'error': 'No token provided'}, status=401)

        try:
            token = auth_header.split(' ')[1]
            AccessToken(token)
            return None
        except (IndexError, TokenError, InvalidToken) as e:
            return JsonResponse({'error': 'Invalid token'}, status=401)
