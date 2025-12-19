from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Loan
from books.serializers import BookListSerializer


class LoanSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Loan
        fields = [
            'id', 'username', 'book', 'borrowed_date', 'due_date',
            'returned_date', 'status', 'is_overdue', 'notes'
        ]
        read_only_fields = [
            'id', 'borrowed_date', 'returned_date', 'status', 'is_overdue'
        ]


class BorrowBookSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    due_date = serializers.DateTimeField(required=False)
    
    def validate_book_id(self, value):
        from books.models import Book
        
        try:
            book = Book.objects.get(id=value)
        except Book.DoesNotExist:
            raise serializers.ValidationError("Book not found.")
        
        if not book.is_available:
            raise serializers.ValidationError("Book is not available for borrowing.")
        
        return value
    
    def validate_due_date(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")
        
        max_due_date = timezone.now() + timedelta(days=30)
        if value and value > max_due_date:
            raise serializers.ValidationError(
                "Due date cannot be more than 30 days from now."
            )
        
        return value
    
    def validate(self, attrs):
        user = self.context['request'].user
        book_id = attrs['book_id']
        
        if Loan.has_active_loan(user, book_id):
            raise serializers.ValidationError({
                'book_id': "You already have an active loan for this book."
            })
        
        # Check if user can borrow more books
        if hasattr(user, 'profile') and not user.profile.can_borrow_books():
            raise serializers.ValidationError({
                'non_field_errors': "You have reached your maximum book limit."
            })
        
        return attrs
    
    def create(self, validated_data):
        from books.models import Book
        
        user = self.context['request'].user
        book = Book.objects.get(id=validated_data['book_id'])
        due_date = validated_data.get('due_date', timezone.now() + timedelta(days=14))
        
        # Decrease available copies
        book.borrow()
        
        # Create loan
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=due_date
        )
        
        return loan


class ReturnBookSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    
    def validate_loan_id(self, value):
        user = self.context['request'].user
        
        try:
            loan = Loan.objects.get(id=value)
        except Loan.DoesNotExist:
            raise serializers.ValidationError("Loan not found.")
        
        # Admin can return any book
        if not user.is_staff and loan.user != user:
            raise serializers.ValidationError("This loan does not belong to you.")
        
        if loan.status == 'returned':
            raise serializers.ValidationError("This book has already been returned.")
        
        return value
    
    def save(self):
        loan = Loan.objects.get(id=self.validated_data['loan_id'])
        loan.return_book()
        return loan


class LoanAdminSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Loan
        fields = [
            'id', 'user_id', 'username', 'book', 'borrowed_date',
            'due_date', 'returned_date', 'status', 'is_overdue', 'notes'
        ]
