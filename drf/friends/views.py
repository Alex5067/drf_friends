from django.shortcuts import render
from rest_framework import generics
from friends.models import Friend, User
from friends.models import FriendRequest
from rest_framework import permissions
from friends.serializers import FriendSerializer, UserSerializer, UserProfileSerializer, AllUsersSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class UserRegister(APIView):
    def post(self, request, format=None):
        username = request.query_params.get('username')
        email = request.query_params.get('email')
        password = request.query_params.get('password')
        serializer = UserSerializer(data={'email': email, 'password': password, 'username': username})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AllUsers(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        current_user = request.user
        users = User.objects.exclude(id=current_user.id)
        serializer = AllUsersSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SendRequestToUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        username = request.query_params.get('username')
        friend = User.objects.get(username=username)
        friend_request = FriendRequest.objects.filter(from_user=request.user, to_user=friend).first()
        if not friend_request:
            reverse_request = FriendRequest.objects.filter(from_user=friend, to_user=request.user).first()
            if reverse_request:
                reverse_request.accept()
                reverse_request.delete()
                return Response("Вы добавили друга")
            else:
                FriendRequest.objects.create(from_user=request.user, to_user=friend)
                return Response("Вы отправили заявку в друзья")
        else:
            return Response("Такая заявка уже существует")

class AcceptRequestFromUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        username = request.query_params.get('username')
        friend = User.objects.get(username=username)
        friend_request = FriendRequest.objects.filter(from_user=friend, to_user=request.user).first()
        if friend_request:
            friend_request.accept()
            friend_request.delete()
            return Response(f"Вы добавили {friend} в друзья")

class RejectRequestFromUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        username = request.query_params.get('username')
        pass



