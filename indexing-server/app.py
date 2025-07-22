import os
import time
import uuid
import ollama
from qdrant_client import QdrantClient, models
from PyPDF2 import PdfReader

# --- Qdrant Configuration ---
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "pdf_embeddings"

# --- Ollama Configuration ---
OLLAMA_MODEL = "nomic-embed-text"

# --- Downloads Folder ---
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")


def get_pdf_text(file_path):
    """Extracts text from a PDF file."""
    try:
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return None


def get_embedding(text):
    """Generates an embedding for the given text using Ollama."""
    try:
        response = ollama.embeddings(model=OLLAMA_MODEL, prompt=text)
        return response["embedding"]
    except Exception as e:
        print(f"Error getting embedding from Ollama: {e}")
        return None


def main():
    """Monitors the Downloads folder and processes new PDFs."""
    print("Starting PDF processing script...")

    # --- Initialize Qdrant Client ---
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        # Check if the collection exists, create it if not
        try:
            client.get_collection(collection_name=COLLECTION_NAME)
            print(f"Collection '{COLLECTION_NAME}' already exists.")
        except Exception:
            client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=768, distance=models.Distance.COSINE
                ),
            )
            print(f"Collection '{COLLECTION_NAME}' created.")
    except Exception as e:
        print(f"Error connecting to Qdrant: {e}")
        return

    # Get the set of files that already exist in the directory at startup
    print("Performing initial scan of Downloads folder...")
    processed_files = {
        f for f in os.listdir(DOWNLOADS_DIR) if f.lower().endswith(".pdf")
    }
    print(
        f"Initial scan complete. {len(processed_files)} PDF files found. Monitoring for new files."
    )

    while True:
        try:
            current_files = {
                f for f in os.listdir(DOWNLOADS_DIR) if f.lower().endswith(".pdf")
            }
            new_files = current_files - processed_files

            for filename in new_files:
                file_path = os.path.join(DOWNLOADS_DIR, filename)
                print(f"New PDF detected: {filename}")

                # 1. Extract text from the PDF
                pdf_text = get_pdf_text(file_path)
                if not pdf_text:
                    processed_files.add(
                        filename
                    )  # Add to set to avoid re-processing on error
                    continue

                # 2. Generate embedding for the text
                embedding = get_embedding(pdf_text)
                print(f"Embedding: {embedding}")
                if not embedding:
                    processed_files.add(
                        filename
                    )  # Add to set to avoid re-processing on error
                    continue

                # 3. Store the embedding in Qdrant
                try:
                    client.upsert(
                        collection_name=COLLECTION_NAME,
                        points=[
                            models.PointStruct(
                                id=str(uuid.uuid4()),
                                vector=embedding,
                                payload={
                                    "filename": filename,
                                    "text": pdf_text[:200] + "...",
                                },  # Store filename and a snippet
                            )
                        ],
                        wait=True,
                    )
                    print(f"Successfully embedded and stored '{filename}' in Qdrant.")
                    processed_files.add(filename)  # Add to the set of processed files
                except Exception as e:
                    print(f"Error storing embedding in Qdrant: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(10)  # Check for new files every 10 seconds


if __name__ == "__main__":
    main()
