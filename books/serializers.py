from rest_framework import serializers
from .models import Book


class BookListSerializer(serializers.ModelSerializer):
    """Serializer for book list view with essential fields."""
    
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'genre',
            'is_available', 'available_copies', 'cover_image'
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed book view."""
    
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'page_count',
            'published_date', 'genre', 'description',
            'total_copies', 'available_copies', 'is_available',
            'cover_image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating books (admin only)."""
    
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'page_count',
            'published_date', 'genre', 'description',
            'total_copies', 'available_copies', 'cover_image'
        ]

    def validate(self, attrs):
        """Ensure available_copies doesn't exceed total_copies."""
        total = attrs.get('total_copies', 1)
        available = attrs.get('available_copies', total)
        
        if available > total:
            raise serializers.ValidationError({
                'available_copies': 'Available copies cannot exceed total copies.'
            })
        
        return attrs

    def create(self, validated_data):
        """Set available_copies to total_copies if not provided."""
        if 'available_copies' not in validated_data:
            validated_data['available_copies'] = validated_data.get('total_copies', 1)
        return super().create(validated_data)
