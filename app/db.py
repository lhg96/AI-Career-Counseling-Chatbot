from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import json
import logging
from typing import List, Dict, Optional
from sqlalchemy.exc import SQLAlchemyError

from app.models import (
    Base, Student, CounsellingSession, Highlight,
    CounsellingRecord, ExpertLabeling, JobInformation
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = 'career_guidance.db', batch_size: int = 100):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.batch_size = batch_size
        self.current_batch = []

    def load_json_file(self, file_path: Path) -> Optional[dict]:
        """Load and parse a JSON file with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in {file_path}: {e}")
            return None
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading {file_path}: {e}")
            return None

    def flush_batch(self):
        """Commit the current batch of records to the database."""
        if self.current_batch:
            try:
                self.session.bulk_save_objects(self.current_batch)
                self.session.commit()
                self.current_batch = []
            except SQLAlchemyError as e:
                logger.error(f"Database error while flushing batch: {e}")
                self.session.rollback()
                raise

    def add_to_batch(self, obj):
        """Add an object to the current batch and flush if batch size is reached."""
        self.current_batch.append(obj)
        if len(self.current_batch) >= self.batch_size:
            self.flush_batch()

    def import_school_data(self, school_level: str, data: List[dict]):
        """Import school-level counselling data with improved error handling and batch processing."""
        if not data:
            logger.warning(f"No data provided for school level: {school_level}")
            return

        total_records = len(data)
        processed = 0
        errors = 0

        for record in data:
            try:
                # Parse expert labeling data
                expert_data = ExpertLabeling.parse_obj(record)
                
                # Create student record
                student = Student(
                    student_idx=expert_data.student_idx,
                    school_level=school_level
                )
                self.session.add(student)
                self.session.flush()  # Get the student ID
                
                # Create counselling sessions
                for summary in expert_data.counselling_summaries:
                    session = CounsellingSession(
                        student_id=student.id,
                        counseling_idx=summary.counseling_idx,
                        summary=summary.summary
                    )
                    self.session.add(session)
                    self.session.flush()  # Get the session ID
                    
                    # Add highlights from the summary
                    for highlight_data in summary.highlights:
                        highlight = Highlight(
                            session_id=session.id,
                            start_idx=highlight_data.start_idx,
                            end_idx=highlight_data.end_idx,
                            content=summary.summary[highlight_data.start_idx:highlight_data.end_idx]
                        )
                        self.add_to_batch(highlight)
                
                processed += 1
                if processed % 10 == 0:  # Log progress every 10 records
                    logger.info(f"Processed {processed}/{total_records} records for {school_level}")
                
            except Exception as e:
                errors += 1
                logger.error(f"Error processing record {record.get('student_idx', 'unknown')}: {e}")
                self.session.rollback()
                continue

        # Flush any remaining batch items
        self.flush_batch()
        
        logger.info(f"Completed processing {school_level} data:")
        logger.info(f"Total processed: {processed}")
        logger.info(f"Total errors: {errors}")

    def process_all_data(self, base_path: Path):
        """Process all data from the given base path with progress tracking."""
        school_levels = {'초등': '01. 초등', '중등': '02. 중등', '고등': '03. 고등'}
        
        for level, folder in school_levels.items():
            try:
                file_path = base_path / '01. 학교급' / folder / f'전문가_라벨링_데이터_{level}학교.json'
                logger.info(f"Processing {level} school data from {file_path}")
                
                if not file_path.exists():
                    logger.warning(f"File not found: {file_path}")
                    continue
                    
                data = self.load_json_file(file_path)
                if data:
                    self.import_school_data(level, data)
                else:
                    logger.error(f"Failed to load data from {file_path}")
            
            except Exception as e:
                logger.error(f"Error processing {level} school data: {e}")
                continue

    def close(self):
        """Safely close the database session."""
        try:
            self.flush_batch()  # Ensure any remaining batch items are saved
            self.session.close()
        except Exception as e:
            logger.error(f"Error while closing database session: {e}")
