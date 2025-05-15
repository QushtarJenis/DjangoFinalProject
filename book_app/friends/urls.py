from django.urls import path
from .views import (
    SearchUserView, SendFriendRequestView, RespondFriendRequestView,
    ListFriendRequestsView, ListFriendsView, FriendsOverviewView, FriendProfileView
)

urlpatterns = [
    path('search', SearchUserView.as_view(), name='search-user'),
    path('request', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('respond', RespondFriendRequestView.as_view(), name='respond-friend-request'),
    path('overview', FriendsOverviewView.as_view(), name='friends-overview'),
    path('profile/<int:user_id>/', FriendProfileView.as_view(), name='friend-profile'),
    path('friend/<int:user_id>/', FriendProfileView.as_view(), name='friend-info'),
] 