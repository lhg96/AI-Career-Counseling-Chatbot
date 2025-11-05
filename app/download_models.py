import os
from pathlib import Path
from sentence_transformers import SentenceTransformer

def download_model():
    MODEL_PATH = Path(__file__).parent / "models" / "all-MiniLM-L6-v2"
    
    if MODEL_PATH.exists():
        print("Model already exists.")
        return
    
    print("Downloading embedding model...")
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    model.save(str(MODEL_PATH))
    print("Model downloaded successfully!")

if __name__ == "__main__":
    download_model()
