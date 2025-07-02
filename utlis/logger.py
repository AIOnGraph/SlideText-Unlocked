import logging

class Logger:
    def __init__(self, level=logging.INFO):
        """Initialize the logger with configuration."""
        self.logger = logging.getLogger(__name__)
        self._configure_logging(level)

    def _configure_logging(self, level: int) -> None:
        """Configure logging settings."""
        logging.basicConfig(
            level=level,  # Set the global logging level here
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def info(self, message: str):
        """Log an info-level message."""
        self.logger.info(message)

    def error(self, message: str):
        """Log an error-level message."""
        self.logger.error(message)

    def debug(self, message: str):
        """Log a debug-level message."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log an warning-level message."""
        self.logger.warning(message)