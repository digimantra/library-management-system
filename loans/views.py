from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Loan
from .serializers import (
    LoanSerializer,
    BorrowBookSerializer,
    ReturnBookSerializer,
    LoanAdminSerializer
)
from accounts.permissions import IsAdminUser


class BorrowBookView(generics.CreateAPIView):
    serializer_class = BorrowBookSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Borrow a book",
        request_body=BorrowBookSerializer,
        responses={
            201: openapi.Response(
                description="Book borrowed successfully",
                schema=LoanSerializer
            ),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Authentication required")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loan = serializer.save()
        
        return Response(
            {
                'message': 'Book borrowed successfully.',
                'loan': LoanSerializer(loan).data
            },
            status=status.HTTP_201_CREATED
        )


class ReturnBookView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Return a borrowed book",
        request_body=ReturnBookSerializer,
        responses={
            200: openapi.Response(
                description="Book returned successfully",
                schema=LoanSerializer
            ),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Authentication required")
        }
    )
    def post(self, request):
        serializer = ReturnBookSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        loan = serializer.save()
        
        return Response(
            {
                'message': 'Book returned successfully.',
                'loan': LoanSerializer(loan).data
            },
            status=status.HTTP_200_OK
        )


class UserLoanHistoryView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['borrowed_date', 'due_date', 'returned_date']
    ordering = ['-borrowed_date']

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user).select_related('book')

    @swagger_auto_schema(
        operation_description="Get user's loan history",
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description="Filter by status (active, returned, overdue)",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ActiveLoansView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(
            user=self.request.user,
            status__in=['active', 'overdue']
        ).select_related('book')


class AdminLoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all().select_related('user', 'book')
    serializer_class = LoanAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'user__id', 'book__id']
    search_fields = ['user__username', 'book__title', 'book__isbn']
    ordering_fields = ['borrowed_date', 'due_date', 'returned_date']
    ordering = ['-borrowed_date']
    http_method_names = ['get', 'head', 'options']  # Read-only
