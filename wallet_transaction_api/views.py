"""Views for the wallet_transaction_api application."""

from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from loguru import logger
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_json_api.django_filters import DjangoFilterBackend
from rest_framework_json_api.filters import OrderingFilter

from .models import Transaction, Wallet
from .serializers import TransactionSerializer, WalletSerializer


class WalletViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Wallet API requests.

    Supports listing, retrieving, creating, updating, and deleting Wallet instances.
    """

    queryset = Wallet.objects.all().order_by("id")  # Ensure ordering
    serializer_class = WalletSerializer
    filterset_fields = ["label"]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Transaction API requests.

    Handles listing, retrieving, creating, updating, and deleting transactions.
    """

    queryset = Transaction.objects.all().order_by("-amount")
    serializer_class = TransactionSerializer
    filterset_fields = ["wallet", "txid", "amount"]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def perform_create(self, serializer):
        try:
            serializer.save()
        except (ValidationError, IntegrityError) as e:
            logger.error(f"Error saving transaction: {e}")
            raise ValidationError({"detail": str(e)})
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ValidationError({"detail": "An unexpected error occurred."})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED, headers=headers
                )
        except (ValidationError, IntegrityError) as e:
            logger.error(f"Validation or IntegrityError occurred: {e}")
            return Response(
                {"errors": [{"detail": str(e)}]}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            return Response(
                {"errors": [{"detail": "An unexpected error occurred."}]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
