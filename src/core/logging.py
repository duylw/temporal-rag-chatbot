# src/core/logging.py
import logging
import sys

class ColorNodeFormatter(logging.Formatter):
    # ANSI color codes
    CYAN = '\033[96m'
    RESET = '\033[0m'

    def format(self, record):
        # Format the log string first
        msg = super().format(record)
        # If the literal "NODE:" is in the message, colorize it
        if "NODE:" in msg:
            msg = msg.replace("NODE:", f"{self.CYAN}NODE:{self.RESET}")
        return msg

def setup_logging():
    # Force standard output to use UTF-8 for Vietnamese characters
    sys.stdout.reconfigure(encoding='utf-8')

    # Create a console handler and attach the custom formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorNodeFormatter('%(levelname)s - %(message)s'))

    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler]
    )