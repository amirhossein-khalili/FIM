# decorators.py

import csv  # Import the csv module
import functools
import os
import sys  # For console fallback
import time

from django.http import HttpRequest
from loguru import logger

# --- Loguru Configuration ---

# Define the base log directory
LOG_DIR = "logs"

# Define CSV Headers
# These are the columns that will appear in the CSV file
# The order here determines the column order in the CSV
CSV_HEADERS = [
    "timestamp",
    "level",
    "view_name",
    "stage",  # e.g., 'entry', 'exit', 'exception'
    "method",
    "path",
    "user",
    "duration_ms",  # Only present for 'exit' stage
    "status_code",  # Only present for 'exit' stage
    "exception_type",  # Only present for 'exception' stage
    "exception_message",  # Only present for 'exception' stage
    # Add other fields as needed, maybe request body/query params carefully
]

# Store file handles to avoid reopening the same file multiple times
# Key: full_file_path, Value: file_object
_file_handles = {}


def write_csv_log(message):
    """
    Custom Loguru sink function to write log records as CSV rows.
    Determines the file path based on view_name and date.
    Format: logs/<view_name>/<date>.csv
    """
    record = message.record

    # This sink is only for view-specific logs, filtered by the presence of 'view_name'
    if "view_name" not in record["extra"]:
        # Loguru's filter should prevent this sink from being called,
        # but this is a safe guard.
        return

    try:
        view_name = record["extra"]["view_name"]
        log_subdir = os.path.join(LOG_DIR, view_name)

        # Ensure the subdirectory for the view exists
        os.makedirs(log_subdir, exist_ok=True)

        # Format the date for the filename and use .csv extension
        log_date = record["time"].strftime("%Y-%m-%d")
        log_file_name = f"{log_date}.csv"
        log_file_path = os.path.join(log_subdir, log_file_name)

        # --- Get or Create File Handle ---
        # Use a global dict to manage file handles.
        # This helps performance by not opening/closing the file for every log message.
        # However, careful handling is needed for application shutdown.
        # Loguru tries to close sinks gracefully on exit.
        if log_file_path not in _file_handles or _file_handles[log_file_path].closed:
            # 'a+' mode allows reading and appending. Used to check if file is empty for headers.
            _file_handles[log_file_path] = open(
                log_file_path, "a+", newline="", encoding="utf-8"
            )
            # Move to the beginning to check file size
            _file_handles[log_file_path].seek(0)
            # Check if file is empty and write header if needed
            if os.path.getsize(log_file_path) == 0:
                writer = csv.writer(_file_handles[log_file_path])
                writer.writerow(CSV_HEADERS)
            # Move back to the end for appending
            _file_handles[log_file_path].seek(0, 2)

        file_handle = _file_handles[log_file_path]

        # --- Prepare CSV Row Data ---
        data = record[
            "extra"
        ]  # Extract the 'extra' dictionary containing structured data
        # Use get() with a default value (None or empty string) to handle missing keys gracefully
        row_data = [
            record["time"].strftime("%Y-%m-%d %H:%M:%S.%f"),  # Timestamp
            record["level"].name,  # Level name (e.g., INFO, ERROR)
            data.get("view_name", ""),
            data.get("stage", ""),
            data.get("method", ""),
            data.get("path", ""),
            data.get("user", ""),
            data.get("duration_ms", ""),
            data.get("status_code", ""),
            data.get("exception_type", ""),
            data.get("exception_message", ""),
            # Add other fields here matching CSV_HEADERS order
        ]

        # --- Write CSV Row ---
        writer = csv.writer(file_handle)
        writer.writerow(row_data)

        # Ensure data is written to disk periodically (optional, performance vs data safety)
        # file_handle.flush()
        # os.fsync(file_handle.fileno())

    except Exception as e:
        # Log errors that occur *within* the sink itself to stderr or a fallback
        # This prevents a sink error from crashing the application without logging
        logger.opt(exception=True).error(f"Error in custom CSV sink: {e}")
        # Fallback: Log the original message to stderr if the sink fails
        print(
            f"Loguru CSV sink failed. Original message: {message['text']}",
            file=sys.stderr,
        )


# Remove default handler(s) if necessary (e.g., console logger setup elsewhere)
# logger.remove()

# Add the custom CSV sink for view-specific logs
# - sink: Uses our function to write the log record as a CSV row.
# - level: Set the minimum level to log (e.g., "INFO").
# - format: Keep minimal, as the sink handles formatting the CSV row from 'extra'.
#   We might still need a format string if the sink itself processes {message},
#   but in our case, the sink uses the 'record' directly. Let's use a simple format
#   or just `{message}` if the custom sink needs the default loguru text.
#   Actually, since the sink receives the full message object, we don't strictly *need*
#   the format string to generate the CSV data, we extract it from 'extra'.
#   Let's set format to "" to keep the loguru-generated text message minimal.
# - enqueue: True makes logging asynchronous (recommended for web apps).
# - filter: Only logs records that have 'view_name' in their extra dict.
logger.add(
    write_csv_log,  # Our custom CSV sink function
    level="INFO",
    format="",  # Format is handled by the custom sink's CSV writer
    enqueue=True,
    filter=lambda record: "view_name" in record["extra"],
    # You might want to add rotation/retention for this sink too, but for a function sink
    # you'd need to implement that logic *inside* the function based on file path.
    # The current logic creates a new file per day, achieving daily separation.
)

# Optional: Add a fallback sink for general logs or errors during path determination
# This sink uses a file path pattern and text format, so 'rotation' is valid here.
# This catches logs *without* 'view_name' or issues in the decorator itself.
logger.add(
    os.path.join(
        LOG_DIR, "general", "general_{time:YYYY-MM-DD}.log"
    ),  # Sink is a file path pattern
    rotation="00:00",  # Rotate the general log file at midnight
    level="INFO",  # Or DEBUG, ERROR etc.
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    enqueue=True,
    filter=lambda record: "view_name"
    not in record["extra"],  # Catch logs without view_name
)

# Optional: Add a console logger for debugging if needed
# logger.add(sys.stderr, level="DEBUG")


# --- Decorator ---


def log_view_details(func):
    """
    A decorator for Django views (function-based or class-based methods)
    that logs request details, execution time, and any exceptions using loguru.
    Logs are routed by the configured loguru sinks (now includes CSV).
    Structured data is passed in the 'extra' dict for CSV formatting.
    """

    @functools.wraps(func)  # Preserves original function metadata
    def wrapper(*args, **kwargs):
        # --- Identify the request object ---
        request = None
        if args and isinstance(args[0], HttpRequest):
            request = args[0]
        elif len(args) > 1 and isinstance(args[1], HttpRequest):
            request = args[1]

        view_name = func.__name__
        user_info = (
            str(request.user)  # Convert user object to string
            if request and hasattr(request, "user") and request.user.is_authenticated
            else "Anonymous"
        )
        request_method = request.method if request else "N/A"
        request_path = request.path if request else "N/A"

        # Base data to bind to the logger for this context
        # This ensures view_name is always available for the sink filter
        bound_logger = logger.bind(
            view_name=view_name,
            method=request_method,  # Pass method and path here for easier access in sink extra
            path=request_path,
            user=user_info,
        )

        # If request object couldn't be identified, log error and attempt execution
        if request is None:
            # Log to the general logger since we don't have full request context for CSV
            bound_logger.error(
                f"Could not find HttpRequest object in decorated view arguments for function '{view_name}'."
            )
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log without full request context, will go to general log
                bound_logger.exception(
                    f"Exception in view '{view_name}' (request object not identified)."
                )
                raise
            # No return None needed as exception is raised or func returns

        # --- Log Entry Details (for CSV 'entry' row) ---
        # Pass structured data in 'extra' for the CSV sink
        bound_logger.info(
            "View Access - Entry",  # Message text (can be simple as sink uses extra)
            extra={
                "stage": "entry",
                # method, path, user are already bound
            },
        )

        # --- Start Timer ---
        start_time = time.time()

        response = None
        exception_details = {}

        try:
            # --- Execute the View ---
            response = func(*args, **kwargs)
        except Exception as e:
            # --- Log Exception (for CSV 'exception' row) ---
            exception_details = {
                "exception_type": type(e).__name__,
                "exception_message": str(e),
            }
            # Log exception using the bound logger to include view_name etc.
            bound_logger.exception(
                "View Access - Exception",  # Message text
                extra={
                    "stage": "exception",
                    **exception_details,  # Include exception details in extra
                    # method, path, user are already bound
                },
            )
            raise  # Re-raise the exception

        finally:
            # This block executes whether there was an exception or not.
            # We log the 'exit' stage here, but need to check if an exception occurred
            # to avoid logging a successful exit if there was an error.
            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)  # ms

            if (
                not exception_details
            ):  # Only log exit if no exception occurred in try block
                status_code = getattr(response, "status_code", "N/A")

                # --- Log Completion (for CSV 'exit' row) ---
                bound_logger.info(
                    "View Access - Exit",  # Message text
                    extra={
                        "stage": "exit",
                        "duration_ms": duration,
                        "status_code": status_code,
                        # method, path, user are already bound
                    },
                )

        return response  # Return the response after logging

    return wrapper


# --- IMPORTANT: Resource Cleanup ---
# Since we are managing file handles manually in write_csv_log,
# it's crucial to ensure they are closed when the application shuts down.
# Loguru has hooks for this. We can use logger.complete() and logger.shutdown().
# A common place to call this in a Django app is during the WSGI server shutdown
# or potentially using Django signals or a custom management command/app config.
# For simple cases, Loguru often attempts graceful shutdown automatically.
# If you encounter issues with files not being closed on shutdown,
# you might need a more explicit cleanup mechanism.

# Example cleanup (less common directly in decorators.py, more in app config/wsgi)
# import atexit
# atexit.register(logger.complete)
# atexit.register(logger.shutdown)

# --- Example Usage in views.py (Decorator usage remains the same) ---

# from django.http import HttpResponse, HttpRequest
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .decorators import log_view_details # Assuming decorators.py is in the same app
# # Loguru logger is configured globally, no need to import logger here unless using it directly
# import time

# # --- Example Function-Based View ---
# @log_view_details
# def my_sample_view(request: HttpRequest):
#     """
#     An example Django function-based view. Logs go to logs/my_sample_view/YYYY-MM-DD.csv
#     """
#     # You can still use logger directly if needed, these won't go to the CSV sink
#     # unless you bind 'view_name' or modify the filter.
#     # logger.debug("Inside my_sample_view logic.")
#     time.sleep(0.1)
#     if 'error' in request.GET:
#         raise ValueError("Simulated error requested!")
#     return HttpResponse(f"Hello from {my_sample_view.__name__}!")

# # --- Example Class-Based View (DRF APIView) ---
# class MySampleAPIView(APIView):
#     """
#     An example DRF APIView. Method logs go to respective directories.
#     GET logs go to logs/get/YYYY-MM-DD.csv, POST to logs/post/YYYY-MM-DD.csv
#     """
#     @log_view_details
#     def get(self, request: HttpRequest, format=None):
#         """
#         Handle GET requests.
#         """
#         time.sleep(0.05)
#         content = {'message': f'Hello from {self.__class__.__name__}.get'}
#         return Response(content, status=status.HTTP_200_OK)

#     @log_view_details
#     def post(self, request: HttpRequest, format=None):
#         """
#         Handle POST requests.
#         """
#         time.sleep(0.08)
#         return Response(request.data, status=status.HTTP_201_CREATED)
