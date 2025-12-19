from django.contrib import admin
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """Admin configuration for Loan model."""
    
    list_display = [
        'id', 'user', 'book', 'borrowed_date', 'due_date',
        'returned_date', 'status', 'is_overdue_display'
    ]
    list_filter = ['status', 'borrowed_date', 'due_date']
    search_fields = ['user__username', 'book__title', 'book__isbn']
    readonly_fields = ['borrowed_date']
    ordering = ['-borrowed_date']
    list_per_page = 25
    raw_id_fields = ['user', 'book']
    date_hierarchy = 'borrowed_date'
    
    fieldsets = (
        ('Loan Information', {
            'fields': ('user', 'book', 'status')
        }),
        ('Dates', {
            'fields': ('borrowed_date', 'due_date', 'returned_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def is_overdue_display(self, obj):
        return obj.is_overdue
    is_overdue_display.short_description = 'Overdue'
    is_overdue_display.boolean = True

    actions = ['mark_as_returned', 'mark_as_overdue']

    @admin.action(description="Mark selected loans as returned")
    def mark_as_returned(self, request, queryset):
        for loan in queryset.filter(status__in=['active', 'overdue']):
            loan.return_book()
        self.message_user(request, "Selected loans have been marked as returned.")

    @admin.action(description="Mark selected loans as overdue")
    def mark_as_overdue(self, request, queryset):
        updated = queryset.filter(status='active').update(status='overdue')
        self.message_user(request, f"{updated} loans marked as overdue.")
