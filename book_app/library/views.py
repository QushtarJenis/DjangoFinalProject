from django.shortcuts import render

from rest_framework import generics
from .models import Book
from .tools import BookPagination
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Category, ReadingProgress
from .serializers import (
    BookSerializer, ReadingProgressSerializer, UserSerializer
)


class BookListAPIView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]
    queryset = Book.objects.filter(qStatus=1)
    serializer_class = BookSerializer
    pagination_class = BookPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    
    filterset_fields = ['title', 'speakerId', 'language', 'hasAudio', 'hasFile', 'year']
    search_fields = ['title', 'shortDescription']
    ordering_fields = ['addTime', 'updateTime', 'title']
    ordering = ['-addTime']

class BookDetailAPIView(generics.RetrieveAPIView):
    queryset = Book.objects.filter(qStatus=1)
    serializer_class = BookSerializer
    lookup_field = 'id'


class BookView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, book_id=None):
        if book_id:
            book = Book.objects.filter(id=book_id, qStatus=1).first()
            if not book:
                return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = BookSerializer(book)
        else:
            books = Book.objects.filter(qStatus=1)
            serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReadingProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, book_id):
        progress, created = ReadingProgress.objects.get_or_create(
            user=request.user,
            book_id=book_id
        )
        serializer = ReadingProgressSerializer(progress)
        return Response(serializer.data)

    def put(self, request, book_id):
        progress = ReadingProgress.objects.get(user=request.user, book_id=book_id)
        serializer = ReadingProgressSerializer(progress, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
