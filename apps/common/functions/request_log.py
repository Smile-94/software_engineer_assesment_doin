from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_request_log(request, message="Request Log"):
    """
    Logs request information: user, device, time, and request data.
    """
    user = request.user if request.user.is_authenticated else "Anonymous"
    # Filter request headers (only readable ones)
    headers = {key: value for key, value in request.META.items() if key.startswith("HTTP_")}

    # Remove Authorization header
    if "HTTP_AUTHORIZATION" in headers:
        headers["HTTP_AUTHORIZATION"] = "[REDACTED]"

    log_data = {
        "message": message,
        "user": str(user),
        "device": request.META.get("HTTP_USER_AGENT", "Unknown Device"),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "headers": headers,
        "method": request.method,
        "path": request.path,
        "ip_address": request.META.get("REMOTE_ADDR"),
        "request_data": request.data if hasattr(request, "data") else {},
        "query_params": dict(request.query_params) if request.query_params else {},
    }

    logger.info(f"INFO:----------->> REQUEST LOG: {log_data}")
    return request
