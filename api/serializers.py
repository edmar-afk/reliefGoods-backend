# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, QrCode, ReliefGoods
from django.db import models


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['purok', 'address', 'family_members', 'profile_picture']
        
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'profile']


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
    
    
class ResidentSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class QrCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QrCode
        fields = ['id', 'resident', 'qr']
        

class ReliefGoodsSerializer(serializers.ModelSerializer):
    claimed_by = UserSerializer(many=True, read_only=True)

    class Meta:
        model = ReliefGoods
        fields = ['id', 'name', 'claimed_by', 'date_issued']
        read_only_fields = ['date_issued']
