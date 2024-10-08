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
from django.contrib import admin
from django.urls import path, include
from friends.views import UserRegister, UserProfile, AllUsers, SendRequestToUser, AcceptRequestFromUser

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('register/', UserRegister.as_view(), name="register"),
    path('accounts/profile/', UserProfile.as_view(), name="profile"),
    path('all_users/', AllUsers.as_view(), name="all_users"),
    path('send_request_to/', SendRequestToUser.as_view(), name="send_request"),
    path('accept_request_from/', AcceptRequestFromUser.as_view(), name="accept_request"),
    #path('reject_request_from', ),

]
