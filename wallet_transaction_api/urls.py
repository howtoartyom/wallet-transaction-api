"""URL configuration for the wallet_transaction_api application."""

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Wallet Transaction API",
        default_version="v1",
        description="API documentation for Wallet Transaction",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourdomain.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(
        "", lambda request: HttpResponseRedirect("/swagger/")
    ),  # Redirect root to Swagger UI
    path("admin/", admin.site.urls),
    path(
        "api/", include("wallet_transaction_api.api_urls")
    ),  # Use the new api_urls file
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
]
