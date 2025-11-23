#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

from scraper import main as scraper_main
from vector_embeddings import VectorEmbeddingSystem, main as embeddings_main
from rag_system import main as rag_main


def run_update(file_path: str) -> bool:
    """Handle the incremental update command."""
    print(f"🔄 Starting incremental update for: {file_path}")

    target = Path(file_path)
    if not target.exists():
        print(f"❌ Error: File does not exist: {file_path}")
        return False

    try:
        system = VectorEmbeddingSystem()
        if not system.load_vector_store():
            print("❌ Error: Could not load existing vector store.")
            print("   Run 'python main.py embed' first to create the index.")
            return False

        success = system.update_document(file_path)
        if success:
            print(f"✅ Successfully updated index for {target.name}")
            stats = system.get_stats()
            print(f"   Total chunks now: {stats['total_chunks']}")
            return True

        print("❌ Update failed. Check logs for details.")
        return False

    except Exception as exc:
        print(f"❌ Unexpected error: {exc}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="NIT Kurukshetra RAG System")
    parser.add_argument("command", choices=["scrape", "embed", "rag", "full", "stats", "update"], help="Command to run")
    parser.add_argument("file", nargs="?", help="File path for update command")
    args = parser.parse_args()

    if args.command == "scrape":
        scraper_main()
        return 0

    if args.command == "embed":
        embeddings_main()
        return 0

    if args.command == "rag":
        rag_main()
        return 0

    if args.command == "update":
        if not args.file:
            print("❌ Error: 'update' command requires a file path.")
            print("Usage: python main.py update extracted_text/some_file.txt")
            return 1
        return 0 if run_update(args.file) else 1

    if args.command == "full":
        scraper_main()
        embeddings_main()
        rag_main()
        return 0

    if args.command == "stats":
        system = VectorEmbeddingSystem()
        if system.load_vector_store():
            print(system.get_stats())
        else:
            print("No vector store found.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
