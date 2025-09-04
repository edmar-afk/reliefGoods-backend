# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
from django.db import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["purok", "address", "profile_picture"]

class RegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)
    password = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)  # will hold family_members

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "profile"]

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        family_members = validated_data.pop("last_name")  # from last_name field
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.create(
            user=user,
            family_members=family_members,
            address=profile_data.get("address"),
            purok=profile_data.get("purok"),
        )
        return user