"""
PDF Semantic Search System

A comprehensive system for indexing and searching PDF documents
using Pinecone vector database with integrated embeddings.
"""

__version__ = "1.0.0"

from .pinecone_manager import PineconeManager
from .pdf_processor import PDFProcessor
from .config import Config

__all__ = ['PineconeManager', 'PDFProcessor', 'Config']
