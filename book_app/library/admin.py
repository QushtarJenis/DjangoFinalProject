from django.contrib import admin
from .models import Book, Category, ReadingProgress

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'year', 'hasAudio', 'hasFile', 'qStatus')
    list_filter = ('language', 'hasAudio', 'hasFile', 'qStatus')
    search_fields = ('title', 'shortDescription')
    ordering = ('-addTime',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'shortDescription', 'language', 'year')
        }),
        ('Media', {
            'fields': ('oldLatynUrl', 'thumbnailUrl', 'oldFileUrl', 'filePath', 'hasAudio', 'hasFile')
        }),
        ('Status', {
            'fields': ('qStatus', 'addTime', 'updateTime')
        }),
        ('Additional', {
            'fields': ('speakerId', 'html'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'last_page', 'is_completed', 'last_read')
    list_filter = ('is_completed',)
    search_fields = ('user__username', 'book__title')
    raw_id_fields = ('user', 'book')
