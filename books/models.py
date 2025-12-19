from django.db import models
from django.core.validators import MinValueValidator, RegexValidator


class Book(models.Model):
    """Model representing a book in the library."""
    
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-Fiction'),
        ('mystery', 'Mystery'),
        ('romance', 'Romance'),
        ('science-fiction', 'Science Fiction'),
        ('fantasy', 'Fantasy'),
        ('thriller', 'Thriller'),
        ('biography', 'Biography'),
        ('history', 'History'),
        ('science', 'Science'),
        ('technology', 'Technology'),
        ('self-help', 'Self-Help'),
        ('children', 'Children'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255, db_index=True)
    author = models.CharField(max_length=255, db_index=True)
    isbn = models.CharField(
        max_length=13,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}(\d{3})?$',
                message='ISBN must be 10 or 13 digits.'
            )
        ],
        help_text='Enter ISBN-10 or ISBN-13'
    )
    page_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    published_date = models.DateField()
    genre = models.CharField(
        max_length=50,
        choices=GENRE_CHOICES,
        default='other',
        db_index=True
    )
    description = models.TextField(blank=True)
    total_copies = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    available_copies = models.PositiveIntegerField(default=1)
    cover_image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        indexes = [
            models.Index(fields=['title', 'author']),
            models.Index(fields=['genre', 'available_copies']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"

    @property
    def is_available(self):
        """Check if the book has available copies."""
        return self.available_copies > 0

    def borrow(self):
        """Decrease available copies when borrowed."""
        if self.available_copies > 0:
            self.available_copies -= 1
            self.save()
            return True
        return False

    def return_book(self):
        """Increase available copies when returned."""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            self.save()
            return True
        return False

    def save(self, *args, **kwargs):
        """Ensure available_copies doesn't exceed total_copies."""
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)
