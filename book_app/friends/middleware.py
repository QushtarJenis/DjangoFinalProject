# friends/middleware.py
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import jwt
from django.conf import settings
import logging

logger = logging.getLogger("channels.jwt")

@database_sync_to_async
def get_user(user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        logger.debug(f"Found user with ID {user_id}: {user.username}")
        return user
    except User.DoesNotExist:
        logger.warning(f"User with ID {user_id} does not exist")
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        path = scope.get('path', '')
        logger.debug(f"WebSocket connection attempt to path: {path}")
        
        query_string = scope.get('query_string', b'').decode()
        logger.debug(f"WebSocket query string: {query_string}")
        
        token = None
        if query_string:
            params = parse_qs(query_string)
            logger.debug(f"Parsed query params: {params}")
            token_list = params.get('token')
            if token_list and token_list[0]:
                token = token_list[0]
                logger.debug(f"Found token in query params")
        
        # Default user is AnonymousUser
        scope['user'] = AnonymousUser()
        
        if token:
            try:
                # Manual JWT decoding to better debug the issue
                logger.debug(f"Attempting to decode token...")
                
                # Decode token without verification first to inspect payload
                unverified_payload = jwt.decode(
                    token, 
                    options={"verify_signature": False}
                )
                logger.debug(f"Unverified token payload: {unverified_payload}")
                
                # Now verify the token
                verified_payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"],
                )
                logger.debug(f"Token verified successfully")
                
                # Get user ID from verified token
                user_id = verified_payload.get('user_id')
                
                if user_id:
                    logger.debug(f"Fetching user with ID: {user_id}")
                    scope['user'] = await get_user(user_id)
                    logger.info(f"Successfully authenticated user ID: {user_id}")
                else:
                    logger.warning("Token payload did not contain user_id")
                    
            except jwt.ExpiredSignatureError:
                logger.error("Token has expired")
            except jwt.InvalidTokenError as e:
                logger.error(f"Invalid token: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        else:
            logger.warning("No token provided in WebSocket connection")
        
        # Log final authentication status
        if isinstance(scope['user'], AnonymousUser):
            logger.warning("WebSocket connection not authenticated")
        else:
            logger.info(f"WebSocket authenticated as user: {scope['user'].username}")
            
        # Continue processing the connection
        return await super().__call__(scope, receive, send)