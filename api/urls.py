from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    path('residents/', views.ResidentListView.as_view(), name='resident-list'),
    
    path('generate-qr/<int:user_id>/', views.GenerateQrCodeView.as_view(), name='generate-qr'),
    path('check-qr/<int:user_id>/', views.CheckQrCodeView.as_view(), name='check-qr'),
    
    path('relief-goods/', views.ReliefGoodsListCreateView.as_view(), name='relief-goods-list-create'),
    
    path("relief-goods/<int:id>/", views.ReliefGoodsDetailView.as_view(), name="relief-goods-detail"),
    path('reliefgoods/<int:pk>/claim/', views.ClaimReliefGoodsView.as_view(), name='claim_relief_goods'),

    path('profile/<int:user_id>/', views.UserProfileView.as_view(), name='user-profile'),
    
    path('relief-goods/<int:id>/delete/', views.DeleteReliefGoodsView.as_view(), name='delete_relief_goods'),

    path('users/', views.AllUsersProfileView.as_view(), name='all-users-profile'),
    
    path('profile/<int:user_id>/upload-picture/', views.UploadProfilePictureView.as_view(), name='upload-profile-picture'),
    
    path('users/delete/<int:pk>/', views.DeleteUserView.as_view(), name='delete-user'),

]
