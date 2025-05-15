# friends/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
import logging

logger = logging.getLogger('channels')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract the friend_id from URL parameter
        self.friend_id = self.scope['url_route']['kwargs']['friend_id']
        self.user = self.scope['user']
        
        # Log detailed connection info
        logger.debug(f"WebSocket connect attempt - Path: {self.scope.get('path', 'unknown')}")
        logger.debug(f"Friend ID: {self.friend_id}")
        logger.debug(f"User authenticated: {not self.user.is_anonymous}")
        
        # Create chat room name
        user_id = self.user.id if not self.user.is_anonymous else 0
        try:
            friend_id = int(self.friend_id)
            self.room_name = f"chat_{min(user_id, friend_id)}_{max(user_id, friend_id)}"
            logger.debug(f"Room name created: {self.room_name}")
        except ValueError:
            logger.error(f"Invalid friend_id: {self.friend_id}")
            await self.accept()
            await self.close(code=4002)
            return
            
        # Accept the connection regardless of authentication status
        await self.accept()
        logger.debug(f"WebSocket connection accepted")

        # Optionally close connection if not authenticated
        if self.user.is_anonymous:
            logger.warning(f"Unauthenticated user - closing connection")
            await self.send(text_data=json.dumps({
                'error': 'Authentication required'
            }))
            # You might want to close or let them stay connected with limited functionality
            # await self.close(code=4001)
            return
            
        # Join room group for authenticated users
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        logger.info(f"User {self.user.username} joined chat room: {self.room_name}")
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'message': f'Connected to chat with friend {self.friend_id}',
            'type': 'system_message'
        }))

    async def disconnect(self, close_code):
        logger.debug(f"WebSocket disconnected with code: {close_code}")
        # Leave room group
        if hasattr(self, 'room_name') and not self.user.is_anonymous:
            await self.channel_layer.group_discard(self.room_name, self.channel_name)
            logger.info(f"User left chat room: {self.room_name}")

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            logger.debug(f"Received message: {text_data[:50]}")
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            
            if self.user.is_anonymous:
                await self.send(text_data=json.dumps({
                    'error': 'Authentication required'
                }))
                return
                
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            )
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
            await self.send(text_data=json.dumps({
                'error': 'Invalid message format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': 'Server error processing message'
            }))

    # Receive message from room group
    async def chat_message(self, event):
        try:
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'user_id': event['user_id'],
                'username': event['username'],
                'type': 'chat_message'
            }))
        except Exception as e:
            logger.error(f"Error sending message to client: {str(e)}")