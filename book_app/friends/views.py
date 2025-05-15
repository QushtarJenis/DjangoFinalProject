from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Friend
from django.db import models
from .serializers import UserSerializer

User = get_user_model()

class SearchUserView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return User.objects.filter(
            models.Q(username__icontains=query) | models.Q(email__icontains=query)
        ).exclude(id=self.request.user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class SendFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        if not receiver_id:
            return Response({'detail': 'receiver_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if int(receiver_id) == request.user.id:
            return Response({'detail': 'Cannot send friend request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            receiver = User.objects.get(id=receiver_id)
            if Friend.objects.filter(requester=request.user, receiver=receiver).exists():
                return Response({'detail': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)
            Friend.objects.create(requester=request.user, receiver=receiver)
            return Response({'detail': 'Friend request sent.'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
class RespondFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        request_id = request.data.get('request_id')
        action = request.data.get('action')  # 'accept' or 'reject'
        if not request_id or action not in ['accept', 'reject']:
            return Response({'detail': 'request_id and valid action are required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            print(request_id, action)
            print(list(Friend.objects.values_list('id', flat=True)))
            friend_request = Friend.objects.get(id=request_id, receiver=request.user, status='pending')
            friend_request.status = 'accepted' if action == 'accept' else 'rejected'
            friend_request.save()
            return Response({'detail': f'Request {action}ed.'})
        except Friend.DoesNotExist:
            return Response({'detail': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

class ListFriendRequestsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        incoming = Friend.objects.filter(receiver=request.user, status='pending')
        outgoing = Friend.objects.filter(requester=request.user, status='pending')
        incoming_data = [
            {
                'id': fr.id,
                'from': {'id': fr.requester.id, 'username': fr.requester.username, 'email': fr.requester.email}
            } for fr in incoming
        ]
        outgoing_data = [
            {
                'id': fr.id,
                'to': {'id': fr.receiver.id, 'username': fr.receiver.username, 'email': fr.receiver.email}
            } for fr in outgoing
        ]
        return Response({'incoming': incoming_data, 'outgoing': outgoing_data})

class ListFriendsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Friends are those with accepted status, either as requester or receiver
        friends = Friend.objects.filter(
            (models.Q(requester=request.user) | models.Q(receiver=request.user)) &
            models.Q(status='accepted')
        )
        friend_users = [
            fr.receiver if fr.requester == request.user else fr.requester
            for fr in friends
        ]
        serializer = UserSerializer(friend_users, many=True)
        return Response(serializer.data)

class FriendsOverviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        friends = Friend.objects.filter(
            (models.Q(requester=request.user) | models.Q(receiver=request.user)) &
            models.Q(status='accepted')
        )
        friend_users = [
            fr.receiver if fr.requester == request.user else fr.requester
            for fr in friends
        ]
        incoming = Friend.objects.filter(receiver=request.user, status='pending')
        incoming_data = [
            {
                'id': fr.id,
                'from': {'id': fr.requester.id, 'username': fr.requester.username, 'email': fr.requester.email}
            } for fr in incoming
        ]
        # Outgoing requests
        outgoing = Friend.objects.filter(requester=request.user, status='pending')
        outgoing_data = [
            {
                'id': fr.id,
                'to': {'id': fr.receiver.id, 'username': fr.receiver.username, 'email': fr.receiver.email}
            } for fr in outgoing
        ]
        # Friends data
        friends_data = [
            {'id': user.id, 'username': user.username, 'email': user.email}
            for user in friend_users
        ]
        return Response({
            'friends': friends_data,
            'incoming': incoming_data,
            'outgoing': outgoing_data
        })

class FriendProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        try:
            friend = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        is_friend = Friend.objects.filter(
            ((models.Q(requester=request.user) & models.Q(receiver=friend)) |
             (models.Q(requester=friend) & models.Q(receiver=request.user))),
            status='accepted'
        ).exists()

        if not is_friend:
            return Response({'error': 'You are not friends with this user'}, status=status.HTTP_403_FORBIDDEN)

        # Return profile info (customize as needed)
        return Response({
            'id': friend.id,
            'username': friend.username,
            'email': friend.email,
            # add more fields as needed
        }) 

