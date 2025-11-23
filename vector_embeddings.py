import os
import json
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:
    import faiss  # type: ignore

    FAISS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    logger.warning("FAISS not available. Incremental updates will be slower/limited.")
    faiss = None  # type: ignore
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer  # type: ignore

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    logger.warning("sentence-transformers not available. Using TF-IDF fallback.")
    SentenceTransformer = None  # type: ignore
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class VectorEmbeddingSystem:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", chunk_size: int = 120, chunk_overlap: int = 15):
        """Initialize the vector embedding system with support for incremental updates."""

        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        if SENTENCE_TRANSFORMERS_AVAILABLE and SentenceTransformer is not None:
            logger.info(f"Loading sentence transformer model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
        else:
            self.model = None
            self.dimension = 768

        if FAISS_AVAILABLE:
            base_index = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIDMap(base_index)
        else:
            self.index = None

        self.metadata: Dict[int, Dict] = {}
        self.manifest: Dict[str, List[int]] = {}
        self.next_chunk_id = 0

        os.makedirs("vector_store", exist_ok=True)

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks: List[str] = []

        step = max(1, self.chunk_size - self.chunk_overlap)
        for i in range(0, len(words), step):
            chunk = " ".join(words[i : i + self.chunk_size]).strip()
            if chunk:
                chunks.append(chunk)

        return chunks

    def _load_single_document(self, file_path: Path) -> Dict:
        """Helper to load and parse one text file."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        url = lines[0].replace("URL: ", "") if lines else "Unknown"
        title = lines[1].replace("Title: ", "") if len(lines) > 1 else "Unknown"

        try:
            separator_idx = next(i for i, line in enumerate(lines) if line.startswith("-" * 10))
            text_content = "\n".join(lines[separator_idx + 1 :])
        except StopIteration:
            text_content = content

        return {
            "url": url,
            "title": title,
            "text": text_content,
            "source_file": str(file_path),
        }

    def load_scraped_data(self) -> List[Dict]:
        """Load all scraped text data from files."""
        documents: List[Dict] = []
        text_dir = Path("extracted_text")

        if not text_dir.exists():
            return documents

        for file_path in text_dir.glob("*.txt"):
            try:
                documents.append(self._load_single_document(file_path))
            except Exception as exc:
                logger.error(f"Error loading {file_path}: {exc}")

        return documents

    def _encode_text(self, text: str) -> np.ndarray:
        if self.model:
            embedding = self.model.encode(text)
        else:
            embedding = np.random.rand(self.dimension)
        return np.array(embedding, dtype="float32")

    def generate_embeddings(self, documents: List[Dict]) -> None:
        """Generate embeddings for all documents from scratch (wipes existing data)."""
        logger.info("Generating embeddings from scratch...")

        if FAISS_AVAILABLE and self.index is not None:
            self.index.reset()
        else:
            if FAISS_AVAILABLE:
                base_index = faiss.IndexFlatL2(self.dimension)
                self.index = faiss.IndexIDMap(base_index)

        self.metadata = {}
        self.manifest = {}
        self.next_chunk_id = 0

        all_embeddings: List[np.ndarray] = []
        all_ids: List[int] = []

        for doc in documents:
            source_file = doc["source_file"]
            self.manifest[source_file] = []
            chunks = self.chunk_text(doc["text"])

            for chunk in chunks:
                if not chunk.strip():
                    continue

                embedding = self._encode_text(chunk)
                chunk_id = self.next_chunk_id
                self.next_chunk_id += 1

                all_embeddings.append(embedding)
                all_ids.append(chunk_id)

                self.metadata[chunk_id] = {
                    "id": chunk_id,
                    "url": doc["url"],
                    "title": doc["title"],
                    "chunk_text": chunk,
                    "source_file": source_file,
                }
                self.manifest[source_file].append(chunk_id)

        if all_embeddings and FAISS_AVAILABLE and self.index is not None:
            self.index.add_with_ids(np.array(all_embeddings), np.array(all_ids, dtype=np.int64))

        logger.info(f"Generated {len(all_ids)} chunks total.")

    def update_document(self, source_file_path: str) -> bool:
        """Atomically update the embeddings for a single document."""
        logger.info(f"🔄 Updating document: {source_file_path}")
        path_obj = Path(source_file_path)

        if not path_obj.exists():
            logger.error(f"File not found: {source_file_path}")
            return False

        old_ids = self.manifest.get(str(path_obj), [])
        if old_ids:
            if FAISS_AVAILABLE and self.index is not None:
                self.index.remove_ids(np.array(old_ids, dtype=np.int64))
            for cid in old_ids:
                self.metadata.pop(cid, None)
            logger.info(f"Removed {len(old_ids)} old chunks.")

        try:
            doc = self._load_single_document(path_obj)
            chunks = self.chunk_text(doc["text"])
        except Exception as exc:
            logger.error(f"Failed to process file: {exc}")
            return False

        new_embeddings: List[np.ndarray] = []
        new_ids: List[int] = []
        self.manifest[str(path_obj)] = []

        for chunk in chunks:
            if not chunk.strip():
                continue

            embedding = self._encode_text(chunk)
            chunk_id = self.next_chunk_id
            self.next_chunk_id += 1

            new_embeddings.append(embedding)
            new_ids.append(chunk_id)

            self.metadata[chunk_id] = {
                "id": chunk_id,
                "url": doc["url"],
                "title": doc["title"],
                "chunk_text": chunk,
                "source_file": str(path_obj),
            }
            self.manifest[str(path_obj)].append(chunk_id)

        if new_embeddings and FAISS_AVAILABLE and self.index is not None:
            self.index.add_with_ids(np.array(new_embeddings), np.array(new_ids, dtype=np.int64))

        logger.info(f"Added {len(new_ids)} new chunks.")
        self.save_vector_store()
        return True

    def save_vector_store(self) -> None:
        """Persist index, metadata, and manifest to disk."""
        if FAISS_AVAILABLE and self.index is not None:
            faiss.write_index(self.index, "vector_store/nitkkr_index.faiss")

        meta_save = {str(k): v for k, v in self.metadata.items()}
        with open("vector_store/metadata.json", "w", encoding="utf-8") as meta_file:
            json.dump(meta_save, meta_file)

        with open("vector_store/manifest.json", "w", encoding="utf-8") as manifest_file:
            json.dump(self.manifest, manifest_file, indent=2)

        info = {
            "next_chunk_id": self.next_chunk_id,
            "model_name": self.model_name,
            "total_chunks": len(self.metadata),
        }
        with open("vector_store/model_info.json", "w", encoding="utf-8") as info_file:
            json.dump(info, info_file, indent=2)

    def load_vector_store(self) -> bool:
        """Load FAISS index, metadata dict, and manifest from disk."""
        try:
            index_path = Path("vector_store/nitkkr_index.faiss")
            if FAISS_AVAILABLE and index_path.exists():
                self.index = faiss.read_index(str(index_path))

            metadata_path = Path("vector_store/metadata.json")
            if metadata_path.exists():
                with metadata_path.open("r", encoding="utf-8") as meta_file:
                    meta_raw = json.load(meta_file)
                    self.metadata = {int(k): v for k, v in meta_raw.items()}

            manifest_path = Path("vector_store/manifest.json")
            if manifest_path.exists():
                with manifest_path.open("r", encoding="utf-8") as manifest_file:
                    self.manifest = json.load(manifest_file)

            info_path = Path("vector_store/model_info.json")
            if info_path.exists():
                with info_path.open("r", encoding="utf-8") as info_file:
                    info = json.load(info_file)
                    self.next_chunk_id = info.get("next_chunk_id", 0)

            return True
        except Exception as exc:
            logger.error(f"Failed to load vector store: {exc}")
            return False

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search using FAISS and retrieve metadata."""
        if not query.strip():
            return []

        if not (self.model and self.index):
            return []

        query_embedding = self.model.encode(query).astype("float32").reshape(1, -1)
        scores, indices = self.index.search(query_embedding, k)

        results: List[Dict] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            metadata = self.metadata.get(int(idx))
            if not metadata:
                continue
            item = metadata.copy()
            item["similarity_score"] = 1.0 / (1.0 + float(score))
            results.append(item)

        return results

    def get_stats(self) -> Dict:
        """Return high-level stats for the vector store."""
        total_chunks = len(self.metadata)
        total_words = sum(len(meta.get("chunk_text", "").split()) for meta in self.metadata.values())
        avg_chunk_length = total_words / total_chunks if total_chunks else 0.0

        return {
            "total_chunks": total_chunks,
            "unique_documents": len(self.manifest),
            "total_words": total_words,
            "average_chunk_length": avg_chunk_length,
            "next_chunk_id": self.next_chunk_id,
            "model_name": self.model_name,
            "embedding_dimension": self.dimension,
        }


def main() -> None:
    system = VectorEmbeddingSystem()
    documents = system.load_scraped_data()
    if not documents:
        logger.error("No documents found. Please run the scraper first.")
        return

    system.generate_embeddings(documents)
    system.save_vector_store()
    stats = system.get_stats()
    logger.info(f"Embedding generation completed. Total chunks: {stats['total_chunks']}")


if __name__ == "__main__":
    main()
