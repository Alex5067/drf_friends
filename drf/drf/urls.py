"""
URL configuration for drf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from friends.views import (
    AcceptRequestFromUser,
    AllUsers,
    DeleteFriend,
    Greetings,
    RejectRequestFromUser,
    SendRequestToUser,
    UserProfile,
    UserRegister,
)
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Friends API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[
        permissions.AllowAny,
    ],
)

urlpatterns = [
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=60), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=60), name="schema-redoc"),
    path("", Greetings.as_view(), name="greetings"),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls"), name="api-auth"),
    path("register/", UserRegister.as_view(), name="register"),
    path("accounts/profile/", UserProfile.as_view(), name="profile"),
    path("all_users/", AllUsers.as_view(), name="all_users"),
    path("send_request_to/", SendRequestToUser.as_view(), name="send_request"),
    path("accept_request_from/", AcceptRequestFromUser.as_view(), name="accept_request"),
    path("reject_request_from/", RejectRequestFromUser.as_view(), name="reject_request"),
    path("delete_friend/", DeleteFriend.as_view(), name="delete_friend"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
