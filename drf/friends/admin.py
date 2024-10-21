from django.contrib import admin
from .models import Friend, FriendRequest

# Register your models here.
admin.site.register(FriendRequest)
admin.site.register(Friend)
