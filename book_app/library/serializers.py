from rest_framework import serializers
from .models import Book, Category, ReadingProgress
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id', 'oldLatynUrl', 'speakerId', 'title', 'shortDescription',
            'thumbnailUrl', 'oldFileUrl', 'filePath', 'hasAudio', 'hasFile',
            'language', 'year', 'addTime', 'updateTime', 'qStatus', 'html'
        ]

class ReadingProgressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    
    class Meta:
        model = ReadingProgress
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
