from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin configuration for Book model."""
    
    list_display = [
        'title', 'author', 'isbn', 'genre',
        'available_copies', 'total_copies', 'is_available_display'
    ]
    list_filter = ['genre', 'published_date', 'created_at']
    search_fields = ['title', 'author', 'isbn', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['title']
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'genre')
        }),
        ('Details', {
            'fields': ('description', 'page_count', 'published_date', 'cover_image')
        }),
        ('Availability', {
            'fields': ('total_copies', 'available_copies')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_available_display(self, obj):
        return obj.is_available
    is_available_display.short_description = 'Available'
    is_available_display.boolean = True
