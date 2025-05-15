# authentication/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import logging

logger = logging.getLogger("http.jwt")

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip authentication for these paths
        if request.path_info.startswith('/admin') or \
           request.path_info.startswith('/static/') or \
           request.path_info == '/favicon.ico' or \
           request.path_info.startswith('/ws/'):  # Skip WebSocket paths
            return None
            
        if request.method == 'OPTIONS':
            return None
        if request.path_info == '/':
            return None

        # Public API paths that don't require authentication
        public_paths = [
            '/api/auth/login',
            '/api/auth/register',
            '/api/auth/token/refresh',
        ]

        current_path = request.path_info.rstrip('/') 
        
        if any(current_path == path or current_path.startswith(path + '/') for path in public_paths):
            return None

        # Check for Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning(f"No token provided for path: {request.path_info}")
            return JsonResponse({'error': 'No token provided'}, status=401)

        try:
            # Extract and validate token
            token_parts = auth_header.split(' ')
            if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
                logger.warning(f"Invalid Authorization header format for path: {request.path_info}")
                return JsonResponse({'error': 'Invalid Authorization header format'}, status=401)
                
            token = token_parts[1]
            
            # Validate token using SimplejWT
            AccessToken(token)
            return None
            
        except (IndexError, TokenError, InvalidToken) as e:
            logger.error(f"Invalid token for path {request.path_info}: {str(e)}")
            return JsonResponse({'error': 'Invalid token'}, status=401)