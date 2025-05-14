from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    id = models.AutoField(primary_key=True)
    oldLatynUrl = models.CharField(max_length=255)
    speakerId = models.IntegerField()
    title = models.CharField(max_length=255)
    shortDescription = models.TextField()
    thumbnailUrl = models.CharField(max_length=255)
    oldFileUrl = models.CharField(max_length=255)
    filePath = models.CharField(max_length=255, null=True, blank=True)
    hasAudio = models.BooleanField(default=False)
    hasFile = models.BooleanField(default=False)
    language = models.CharField(max_length=255, default='kz')
    year = models.CharField(max_length=255, default='0000')
    addTime = models.IntegerField()
    updateTime = models.IntegerField()
    qStatus = models.BooleanField(default=False)
    html = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'book'

class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_progress')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reading_progress')
    last_page = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    last_read = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

