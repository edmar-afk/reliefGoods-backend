from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, ProfileSerializer, ResidentSerializer, UserSerializer, QrCodeSerializer, ReliefGoodsSerializer
from .models import Profile, QrCode, ReliefGoods
from django.shortcuts import get_object_or_404
import qrcode
import io
from django.core.files.base import ContentFile

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the JWT itself
        token['id'] = user.id
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add extra user fields to the response
        data['id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['is_staff'] = self.user.is_staff
        data['is_superuser'] = self.user.is_superuser

        return data



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny] # 👈 anyone can access this endpoint
 
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
class ResidentListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResidentSerializer

    def get_queryset(self):
        return User.objects.filter(is_staff=False, is_superuser=False)
    

class GenerateQrCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        qr_code = QrCode.objects.filter(resident=user).first()
        if qr_code:
            serializer = QrCodeSerializer(qr_code)
            return Response({
                "detail": "QR code already exists",
                "qr": serializer.data["qr"]
            }, status=status.HTTP_200_OK)

        # Only store user_id as QR data
        qr_data = str(user.id)

        qr_img = qrcode.make(qr_data)
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        file_name = f"user_{user.id}_qr.png"

        qr_code = QrCode(resident=user)
        qr_code.qr.save(file_name, ContentFile(buffer.getvalue()), save=True)

        serializer = QrCodeSerializer(qr_code)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
class CheckQrCodeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        qr_code = QrCode.objects.filter(resident=user).first()
        if qr_code:
            serializer = QrCodeSerializer(qr_code, context={"request": request})
            return Response({
                "has_qr": True,
                "qr": serializer.data["qr"]
            }, status=status.HTTP_200_OK)
        else:
            return Response({"has_qr": False, "qr": None}, status=status.HTTP_200_OK)


class ReliefGoodsListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = ReliefGoods.objects.all().order_by('-date_issued')
    serializer_class = ReliefGoodsSerializer


class ReliefGoodsDetailView(generics.RetrieveAPIView):
    queryset = ReliefGoods.objects.all()
    serializer_class = ReliefGoodsSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"
    
class ClaimReliefGoodsView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, pk):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        relief_goods = get_object_or_404(ReliefGoods, pk=pk)
        user = get_object_or_404(User, pk=user_id)

        if user in relief_goods.claimed_by.all():
            return Response({"detail": "This user already claimed this relief good."}, status=status.HTTP_400_BAD_REQUEST)

        relief_goods.claimed_by.add(user)
        relief_goods.save()

        serializer = ReliefGoodsSerializer(relief_goods)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        profile = Profile.objects.filter(user=user).first()
        qr_code = QrCode.objects.filter(resident=user).first()

        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile": {
                "purok": profile.purok if profile else None,
                "address": profile.address if profile else None,
                "family_members": profile.family_members if profile else None,
                "profile_picture": request.build_absolute_uri(profile.profile_picture.url) if profile and profile.profile_picture else None,
            },
            "qr_code": request.build_absolute_uri(qr_code.qr.url) if qr_code and qr_code.qr else None,
        }

        return Response(data, status=status.HTTP_200_OK)
    

class DeleteReliefGoodsView(APIView):
    permission_classes = [AllowAny]
    def delete(self, request, id):
        relief_goods = get_object_or_404(ReliefGoods, id=id)
        relief_goods.delete()
        return Response({"message": "Relief goods deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class AllUsersProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.filter(is_superuser=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UploadProfilePictureView(APIView):
    permission_classes = [AllowAny]
    def put(self, request, user_id):
        profile = get_object_or_404(Profile, user__id=user_id)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DeleteUserView(APIView):
    permission_classes = [AllowAny]
    
    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({"message": "User deleted"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)