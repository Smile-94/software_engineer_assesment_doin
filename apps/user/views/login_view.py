import logging

from django.contrib.auth import authenticate
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from _library.error_codes import INTERNAL_SERVER_ERROR
from _library.functions.device import get_browser_fingerprint, get_device_id
from _library.functions.formatters import response_formatter
from _library.functions.generate_token import (
    generate_raw_token,
    get_access_token_expiry,
    get_refresh_token_expiry,
    hash_token,
    validate_token_signature,
)
from apps.user.models.user_model import UserDeviceToken

logger = logging.getLogger(__name__)


class TokenObtainView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            device_id, is_new_device = get_device_id(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            browser_fingerprint = get_browser_fingerprint(request)

            user = authenticate(username=username, password=password)
            if not user:
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate tokens
            raw_access = generate_raw_token()
            raw_refresh = generate_raw_token()

            # Hash tokens & device info
            access_hash = hash_token(raw_access)
            refresh_hash = hash_token(raw_refresh)
            ua_hash = hash_token(user_agent)
            fingerprint_hash = hash_token(browser_fingerprint)

            # Invalidate old tokens for this device
            UserDeviceToken.objects.filter(user=user, device_id=device_id).update(is_active=False)

            # Save new token
            token_obj = UserDeviceToken.objects.create(
                user=user,
                device_id=device_id,
                access_token_hash=access_hash,
                refresh_token_hash=refresh_hash,
                browser_fingerprint=fingerprint_hash,
                user_agent_hash=ua_hash,
                user_agent=user_agent,
                ip_address=request.META.get("REMOTE_ADDR"),
                access_expires_at=get_access_token_expiry(),
                refresh_expires_at=get_refresh_token_expiry(),
            )

            data = {
                "access_token": raw_access,
                "refresh_token": raw_refresh,
                "access_expires_at": token_obj.access_expires_at,
                "refresh_expires_at": token_obj.refresh_expires_at,
                "device_id": device_id,
                "browser_fingerprint": browser_fingerprint,  # include this for client
            }

            response = Response(data, status=status.HTTP_200_OK)

            if is_new_device:
                response.set_cookie(
                    key="device_id",
                    value=device_id,
                    max_age=60 * 60 * 24 * 365,
                    httponly=True,
                    secure=True,
                    samesite="Lax",
                )

            return response
        except Exception as e:
            logger.exception(f"ERROR:----------->> Login View error: {e}")
            return response_formatter(INTERNAL_SERVER_ERROR)


class TokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            device_id = request.headers.get("X-Device-ID")
            browser_fingerprint = request.headers.get("X-Browser-Fingerprint")
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            if not refresh_token or not device_id or not browser_fingerprint:
                return Response(
                    {"detail": "Missing refresh token or device headers"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate signature
            raw_refresh = validate_token_signature(refresh_token)
            if not raw_refresh:
                return Response(
                    {"detail": "Invalid refresh token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            refresh_hash = hash_token(raw_refresh)

            # Lookup token record
            try:
                token_obj = UserDeviceToken.objects.get(
                    refresh_token_hash=refresh_hash,
                    device_id=device_id,
                    is_active=True,
                )
            except UserDeviceToken.DoesNotExist:
                return Response(
                    {"detail": "Invalid or inactive refresh token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Expiry check
            if token_obj.refresh_expires_at < now():
                token_obj.is_active = False
                token_obj.save(update_fields=["is_active"])
                return Response(
                    {"detail": "Refresh token expired"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Device binding checks
            if token_obj.browser_fingerprint != hash_token(browser_fingerprint):
                return Response(
                    {"detail": "Device fingerprint mismatch"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if token_obj.user_agent_hash != hash_token(user_agent):
                return Response(
                    {"detail": "User agent mismatch"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Rotate tokens
            new_access = generate_raw_token()
            new_refresh = generate_raw_token()

            token_obj.access_token_hash = hash_token(new_access)
            token_obj.refresh_token_hash = hash_token(new_refresh)
            token_obj.access_expires_at = get_access_token_expiry()
            token_obj.refresh_expires_at = get_refresh_token_expiry()
            token_obj.rotated_at = now()
            token_obj.save()

            return Response(
                {
                    "access_token": new_access,
                    "refresh_token": new_refresh,
                    "access_expires_at": token_obj.access_expires_at,
                    "refresh_expires_at": token_obj.refresh_expires_at,
                },
                status=status.HTTP_200_OK,
            )

        except Exception:
            logger.exception(f"ERROR:----------->> Refresh token error: {e}")
            return response_formatter(INTERNAL_SERVER_ERROR)
