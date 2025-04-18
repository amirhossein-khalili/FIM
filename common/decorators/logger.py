import functools
import time

from django.http import HttpRequest  # Import HttpRequest for type checking
from loguru import logger


def     log_view_details(func):
    """
    A decorator for Django views (function-based or class-based methods)
    that logs request details, execution time, and any exceptions using loguru.
    """

    @functools.wraps(func)  # Preserves original function metadata
    def wrapper(*args, **kwargs):
        # --- Identify the request object ---
        # args[0] could be 'request' (for function views) or 'self' (for class methods)
        # args[1] would be 'request' if args[0] is 'self'
        if args and isinstance(args[0], HttpRequest):
            request = args[0]
            view_instance = None  # Function-based view
        elif len(args) > 1 and isinstance(args[1], HttpRequest):
            request = args[1]
            view_instance = args[0]  # Class-based view instance ('self')
        else:
            # Fallback or error handling if request object cannot be found
            # This might happen with decorators applied in unusual ways.
            logger.error(
                "Could not find HttpRequest object in decorated view arguments."
            )
            # Attempt to execute the function anyway, but logging might be incomplete.
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    f"Exception in view '{func.__name__}' (request object not identified)."
                )
                raise
            return None  # Or raise an error if request is strictly required

        # --- Start Timer ---
        start_time = time.time()

        # --- Log Request Details ---
        view_name = func.__name__
        # Use request.user now that 'request' is correctly identified
        user_info = (
            f"User: {request.user}"
            if hasattr(request, "user") and request.user.is_authenticated
            else "User: Anonymous"
        )
        request_info = f"Method: {request.method}, Path: {request.path}, {user_info}"

        logger.info(f"Entering view: '{view_name}'. Request: {request_info}")
        # Optionally log args and kwargs if needed (be careful with sensitive data)
        # logger.debug(f"View args: {args}, kwargs: {kwargs}")

        response = None
        exception_info = None
        try:
            # --- Execute the View ---
            # Pass the original arguments along
            response = func(*args, **kwargs)
            # Note: We don't return response here yet, need to log completion in finally
        except Exception as e:
            # --- Log Exception ---
            exception_info = f"Exception: {type(e).__name__}: {e}"
            logger.exception(
                f"Exception in view '{view_name}'. {request_info}"
            )  # Log exception with traceback
            raise  # Re-raise the exception so Django handles it
        finally:
            # --- Log Completion ---
            end_time = time.time()
            duration = round(
                (end_time - start_time) * 1000, 2
            )  # Duration in milliseconds

            # Get status code from response if it exists and has the attribute
            status_code = getattr(
                response, "status_code", "N/A (Exception or no response)"
            )
            completion_log = (
                f"Exiting view: '{view_name}'. "
                f"Duration: {duration}ms. "
                f"Status Code: {status_code}. "
                f"{request_info}"
            )

            if exception_info:
                # If an exception occurred, it's already logged by logger.exception
                pass  # Avoid duplicate logging
            else:
                # Log successful completion
                logger.info(completion_log)

        return response  # Return the response after logging

    return wrapper
