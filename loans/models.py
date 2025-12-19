from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from books.models import Book


class Loan(models.Model):
    """Model representing a book loan."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='loans'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='loans'
    )
    borrowed_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-borrowed_date']
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['book', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"

    def save(self, *args, **kwargs):
        """Set default due date if not provided."""
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if the loan is overdue."""
        if self.status == 'returned':
            return False
        return timezone.now() > self.due_date

    def return_book(self):
        """Process book return."""
        if self.status == 'active' or self.status == 'overdue':
            self.returned_date = timezone.now()
            self.status = 'returned'
            self.book.return_book()
            self.save()
            return True
        return False

    def update_status(self):
        """Update loan status based on current state."""
        if self.status == 'active' and self.is_overdue:
            self.status = 'overdue'
            self.save()

    @classmethod
    def get_active_loans_count(cls, user):
        """Get count of active loans for a user."""
        return cls.objects.filter(user=user, status='active').count()

    @classmethod
    def has_active_loan(cls, user, book):
        """Check if user has an active loan for a specific book."""
        return cls.objects.filter(
            user=user,
            book=book,
            status__in=['active', 'overdue']
        ).exists()
