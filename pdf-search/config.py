"""
Configuration management for PDF search system.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Configuration for Pinecone PDF search system."""

    # Pinecone Settings
    PINECONE_API_KEY: str = os.getenv('PINECONE_API_KEY', '')
    PINECONE_ENVIRONMENT: str = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
    PINECONE_INDEX_NAME: str = os.getenv('PINECONE_INDEX_NAME', 'sociology-pdfs')
    PINECONE_NAMESPACE: str = os.getenv('PINECONE_NAMESPACE', 'default')

    # Embedding Settings
    EMBEDDING_MODEL: str = os.getenv('EMBEDDING_MODEL', 'llama-text-embed-v2')
    EMBEDDING_DIMENSION: int = int(os.getenv('EMBEDDING_DIMENSION', '1024'))

    # PDF Processing
    CHUNK_SIZE: int = int(os.getenv('CHUNK_SIZE', '1000'))
    CHUNK_OVERLAP: int = int(os.getenv('CHUNK_OVERLAP', '200'))
    MAX_CHUNKS_PER_PDF: int = int(os.getenv('MAX_CHUNKS_PER_PDF', '1000'))

    # Search Settings
    DEFAULT_TOP_K: int = int(os.getenv('DEFAULT_TOP_K', '5'))
    SIMILARITY_THRESHOLD: float = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    MATERIALS_DIR: Path = BASE_DIR / 'materials'
    MANIFEST_PATH: Path = MATERIALS_DIR / 'manifest.json'

    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """
        Validate configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not cls.PINECONE_API_KEY:
            return False, "PINECONE_API_KEY is not set"

        if not cls.PINECONE_INDEX_NAME:
            return False, "PINECONE_INDEX_NAME is not set"

        if cls.CHUNK_SIZE < 100:
            return False, "CHUNK_SIZE must be at least 100"

        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            return False, "CHUNK_OVERLAP must be less than CHUNK_SIZE"

        if not cls.MANIFEST_PATH.exists():
            return False, f"Manifest file not found at {cls.MANIFEST_PATH}"

        return True, None

    @classmethod
    def print_config(cls):
        """Print current configuration (hide sensitive data)."""
        print("=== PDF Search Configuration ===")
        print(f"Pinecone API Key: {'*' * 20}{cls.PINECONE_API_KEY[-4:] if cls.PINECONE_API_KEY else 'NOT SET'}")
        print(f"Pinecone Environment: {cls.PINECONE_ENVIRONMENT}")
        print(f"Index Name: {cls.PINECONE_INDEX_NAME}")
        print(f"Namespace: {cls.PINECONE_NAMESPACE}")
        print(f"Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"Embedding Dimension: {cls.EMBEDDING_DIMENSION}")
        print(f"Chunk Size: {cls.CHUNK_SIZE} chars")
        print(f"Chunk Overlap: {cls.CHUNK_OVERLAP} chars")
        print(f"Default Top-K: {cls.DEFAULT_TOP_K}")
        print(f"Similarity Threshold: {cls.SIMILARITY_THRESHOLD}")
        print(f"Manifest Path: {cls.MANIFEST_PATH}")
        print("=" * 35)


if __name__ == "__main__":
    # Test configuration
    is_valid, error = Config.validate()
    if is_valid:
        Config.print_config()
        print("✓ Configuration is valid")
    else:
        print(f"✗ Configuration error: {error}")
