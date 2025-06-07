import logging
from datetime import datetime
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from collections import defaultdict
import time


# Get an instance of a logger specifically for request logging.
# This logger will be configured in your settings.py to write to a file.
request_logger = logging.getLogger('request_logger')

class RequestLoggingMiddleware:
    """
    Middleware to log details of each incoming HTTP request.
    It logs the timestamp, user (authenticated username or 'Anonymous'),
    and the request path.
    """
    def __init__(self, get_response):
        """
        Initializes the middleware.
        `get_response` is a callable that takes a request and returns a response.
        It typically refers to the next middleware in the chain or the view itself.
        """
        self.get_response = get_response
        # This will be called once when the web server starts.
        # You can perform any one-time setup here.
        request_logger.info("RequestLoggingMiddleware initialized and ready to log requests.")

    def __call__(self, request):
        """
        This method is called for every incoming request.
        It processes the request before it reaches the view,
        and then processes the response after the view has been called.
        """
        # --- Request Processing (before the view is called) ---

        # Get the current timestamp
        timestamp = datetime.now()

        # Determine the user.
        # `request.user` will be an instance of `User` if authenticated,
        # or `AnonymousUser` if not.
        user_info = "Anonymous"
        if request.user.is_authenticated:
            user_info = request.user.username
            # You could also use request.user.email or request.user.id
            # depending on what user identifier you prefer to log.

        # Get the requested path
        request_path = request.path

        # Format the log message
        log_message = f"{timestamp} - User: {user_info} - Path: {request_path}"

        # Log the message using our dedicated logger
        request_logger.info(log_message)

        # Call the next middleware or the view function
        response = self.get_response(request)

        # --- Response Processing (after the view has been called) ---
        # You could add logic here to log response details if needed.

        return response
    
class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        # Allow access only between 18:00 (6PM) and 21:00 (9PM)
        if request.path.startswith('/messaging/') and not (18 <= current_hour < 21):
            return HttpResponseForbidden("Access to the messaging app is restricted at this time.")
        
        return self.get_response(request)
    
class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Track messages by IP: {ip: [(timestamp1), (timestamp2), ...]}
        self.ip_message_log = defaultdict(list)
        self.time_window = 60  # seconds
        self.message_limit = 5

    def __call__(self, request):
        # Only apply to chat message POST requests
        if request.method == 'POST' and request.path.startswith('/messaging/'):
            ip = self.get_client_ip(request)
            current_time = time.time()
            
            # Remove timestamps older than 1 minute
            self.ip_message_log[ip] = [
                ts for ts in self.ip_message_log[ip]
                if current_time - ts < self.time_window
            ]

            if len(self.ip_message_log[ip]) >= self.message_limit:
                return JsonResponse(
                    {"error": "Rate limit exceeded. Max 5 messages per minute."},
                    status=429
                )

            # Log this message timestamp
            self.ip_message_log[ip].append(current_time)

        return self.get_response(request)

    def get_client_ip(self, request):
        """Extracts IP address from request headers."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define paths or actions you want to protect
        protected_paths = ['/admin-action/', '/moderator-only/']

        if request.path in protected_paths:
            user = getattr(request, 'user', None)
            if not user or not user.is_authenticated:
                return HttpResponseForbidden("Access denied: You must be logged in.")

            # Assuming 'role' is a field in the user model or accessible via profile
            user_role = getattr(user, 'role', None)
            if user_role not in ['admin', 'moderator']:
                return HttpResponseForbidden("Access denied: Admin or Moderator role required.")

        return self.get_response(request)
