from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from users.views.oauth_views import (KakaoLoginCallbackView, LogoutView,
                                     RefreshAccessTokenAPIView)

app_name = "users"
urlpatterns = [
    path(
        "login/kakao/callback/", KakaoLoginCallbackView.as_view(), name="kakao_callback"
    ),
    path("token/refresh/", RefreshAccessTokenAPIView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),  # ✅ 추가
    path("logout/", LogoutView.as_view(), name="logout"),

]
