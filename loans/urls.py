from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BorrowBookView,
    ReturnBookView,
    UserLoanHistoryView,
    ActiveLoansView,
    AdminLoanViewSet
)

router = DefaultRouter()
router.register(r'admin', AdminLoanViewSet, basename='admin-loan')

urlpatterns = [
    # User loan endpoints
    path('borrow/', BorrowBookView.as_view(), name='borrow-book'),
    path('return/', ReturnBookView.as_view(), name='return-book'),
    path('history/', UserLoanHistoryView.as_view(), name='loan-history'),
    path('active/', ActiveLoansView.as_view(), name='active-loans'),
    
    # Admin loan management
    path('', include(router.urls)),
]
