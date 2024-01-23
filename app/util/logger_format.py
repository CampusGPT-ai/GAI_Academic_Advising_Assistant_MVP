import logging

# Define the emoji and color codes
LOG_COLORS = {
    "INFO": "\033[92m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "CRITICAL": "\033[91m",  # Red
    "DEBUG": "\033[94m",  # Blue
}

# End color code
ENDC = "\033[0m"

# Custom formatter class
class CustomFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = f"{LOG_COLORS[record.levelname]}{record.levelname}{ENDC}: [%(asctime)s] %(message)s "

        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

