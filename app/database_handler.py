from pathlib import Path
import logging
import sys

from app.db import DatabaseManager  # Changed from 'from db import DatabaseManager'
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_import.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    base_path = Path(__file__).parent.parent / 'data' / '02.라벨링데이터'
    
    if not base_path.exists():
        logger.error(f"Data directory not found: {base_path}")
        return
    
    logger.info("Starting database import process...")
    
    try:
        db = DatabaseManager()
        db.process_all_data(base_path)
        logger.info("Database creation and data import completed successfully")
    except Exception as e:
        logger.error(f"Fatal error occurred during import: {e}")
        raise
    finally:
        try:
            db.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error while closing database: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)
