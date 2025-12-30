#!/usr/bin/env python3
"""
Create Pinecone index for PDF search.

Usage:
    python scripts/create_index.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pinecone_manager import PineconeManager
from config import Config


def main():
    """Create Pinecone index."""
    print("=== Creating Pinecone Index ===\n")

    # Validate configuration
    is_valid, error = Config.validate()
    if not is_valid:
        print(f"✗ Configuration error: {error}")
        print("\nPlease check your .env file")
        return 1

    Config.print_config()
    print()

    # Initialize manager
    try:
        manager = PineconeManager()
        print("✓ Pinecone manager initialized\n")
    except Exception as e:
        print(f"✗ Failed to initialize Pinecone: {e}")
        return 1

    # Create index
    try:
        manager.create_index(
            dimension=Config.EMBEDDING_DIMENSION,
            metric="cosine",
            cloud="aws",
            region=Config.PINECONE_ENVIRONMENT
        )

        print("\n✓ Index created successfully!")
        print(f"\nIndex name: {Config.PINECONE_INDEX_NAME}")
        print(f"Dimension: {Config.EMBEDDING_DIMENSION}")
        print(f"Namespace: {Config.PINECONE_NAMESPACE}")

        # Show stats
        stats = manager.get_index_stats()
        print(f"\nIndex stats:")
        print(f"  Total vectors: {stats['total_vector_count']}")
        print(f"  Dimension: {stats['dimension']}")

        return 0

    except Exception as e:
        print(f"\n✗ Failed to create index: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
