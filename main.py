"""
ReqCockpit - Multi-Partner Requirements Aggregation Tool
Main application entry point
"""
import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from config import APP_NAME, APP_VERSION, LOG_FILE, LOG_LEVEL
from ui.main_window import MainWindow


def setup_logging():
    """Configure application logging"""
    log_file = Path(LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    return logger


def main():
    """Main application entry point"""
    # Setup logging
    logger = setup_logging()
    
    try:
        # Create application
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        logger.info("Application started successfully")
        
        # Run event loop
        sys.exit(app.exec())
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
