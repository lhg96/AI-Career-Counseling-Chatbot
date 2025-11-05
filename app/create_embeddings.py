import json
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
import logging
from tqdm import tqdm
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean text by removing excessive whitespace and special characters."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_school_data(file_path: Path, collection):
    """Process school level counseling data and add to Chroma collection."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for record in tqdm(data, desc=f"Processing {file_path.parent.name}"):
            student_idx = record['student_idx']
            
            for summary in record['counselling_summaries']:
                # Clean and prepare the text
                clean_summary = clean_text(summary['summary'])
                
                # Create metadata
                metadata = {
                    'student_idx': student_idx,
                    'counseling_idx': summary['counseling_idx'],
                    'school_level': file_path.parent.name,
                    'data_type': 'counselling_summary'
                }
                
                # Add document to collection
                collection.add(
                    documents=[clean_summary],
                    metadatas=[metadata],
                    ids=[f"{student_idx}_{summary['counseling_idx']}"]
                )
                
                # Process highlights separately
                for idx, highlight in enumerate(summary['highlights']):
                    highlight_text = clean_text(
                        summary['summary'][highlight['start_idx']:highlight['end_idx']]
                    )
                    
                    highlight_metadata = {
                        'student_idx': student_idx,
                        'counseling_idx': summary['counseling_idx'],
                        'school_level': file_path.parent.name,
                        'data_type': 'highlight',
                        'start_idx': highlight['start_idx'],
                        'end_idx': highlight['end_idx']
                    }
                    
                    collection.add(
                        documents=[highlight_text],
                        metadatas=[highlight_metadata],
                        ids=[f"{student_idx}_{summary['counseling_idx']}_highlight_{idx}"]
                    )
                    
        logger.info(f"Successfully processed {file_path.name}")
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        raise

def main():
    # Initialize Chroma client
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Use sentence-transformers all-MiniLM-L6-v2 model for embeddings
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="./app/models/all-MiniLM-L6-v2"
    )
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="counselling_data",
        embedding_function=embedding_function,
        metadata={"description": "Student counselling data and highlights"}
    )
    
    # Process school level data
    base_path = Path(__file__).parent.parent / 'data' / '02.라벨링데이터' / '01. 학교급'
    school_levels = {
        '초등': '01. 초등/전문가_라벨링_데이터_초등학교.json',
        '중등': '02. 중등/전문가_라벨링_데이터_중학교.json',
        '고등': '03. 고등/전문가_라벨링_데이터_고등학교.json'
    }
    
    for level_name, file_path in school_levels.items():
        full_path = base_path / file_path
        if full_path.exists():
            logger.info(f"Processing {level_name} school data...")
            process_school_data(full_path, collection)
        else:
            logger.warning(f"File not found: {full_path}")
    
    # Print collection statistics
    collection_stats = collection.count()
    logger.info(f"Total documents in collection: {collection_stats}")

if __name__ == "__main__":
    main()