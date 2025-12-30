"""
PDF Processor for extracting and chunking PDF content.
Handles downloading from Google Drive and text extraction.
"""

import io
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import Config


class PDFProcessor:
    """Processes PDFs: download, extract text, and chunk into segments."""

    def __init__(
        self,
        chunk_size: int = Config.CHUNK_SIZE,
        chunk_overlap: int = Config.CHUNK_OVERLAP,
        max_chunks: int = Config.MAX_CHUNKS_PER_PDF
    ):
        """
        Initialize PDF processor.

        Args:
            chunk_size: Size of each text chunk in characters
            chunk_overlap: Overlap between consecutive chunks
            max_chunks: Maximum chunks per PDF (safety limit)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunks = max_chunks

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def download_from_google_drive(
        self,
        file_id: str,
        output_path: Optional[Path] = None
    ) -> bytes:
        """
        Download PDF from Google Drive.

        Args:
            file_id: Google Drive file ID
            output_path: Optional path to save the PDF

        Returns:
            PDF content as bytes
        """
        # Google Drive direct download URL
        url = f"https://drive.google.com/uc?export=download&id={file_id}"

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            pdf_content = response.content

            # Save to file if requested
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(pdf_content)

            return pdf_content

        except requests.RequestException as e:
            raise Exception(f"Failed to download PDF: {e}")

    def extract_text_pypdf2(self, pdf_content: bytes) -> str:
        """
        Extract text using PyPDF2.

        Args:
            pdf_content: PDF file content as bytes

        Returns:
            Extracted text
        """
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is not installed. Run: pip install PyPDF2")

        text = []
        pdf_file = io.BytesIO(pdf_content)

        try:
            reader = PyPDF2.PdfReader(pdf_file)

            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(f"--- Page {page_num + 1} ---\n{page_text}")
                except Exception as e:
                    print(f"Warning: Could not extract page {page_num + 1}: {e}")

            return "\n\n".join(text)

        except Exception as e:
            raise Exception(f"Failed to extract text with PyPDF2: {e}")

    def extract_text_pdfplumber(self, pdf_content: bytes) -> str:
        """
        Extract text using pdfplumber (usually better quality).

        Args:
            pdf_content: PDF file content as bytes

        Returns:
            Extracted text
        """
        if pdfplumber is None:
            raise ImportError("pdfplumber is not installed. Run: pip install pdfplumber")

        text = []
        pdf_file = io.BytesIO(pdf_content)

        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    except Exception as e:
                        print(f"Warning: Could not extract page {page_num + 1}: {e}")

            return "\n\n".join(text)

        except Exception as e:
            raise Exception(f"Failed to extract text with pdfplumber: {e}")

    def extract_text(
        self,
        pdf_content: bytes,
        method: str = "pdfplumber"
    ) -> str:
        """
        Extract text from PDF using specified method.

        Args:
            pdf_content: PDF file content as bytes
            method: Extraction method ('pdfplumber' or 'pypdf2')

        Returns:
            Extracted text
        """
        if method == "pdfplumber":
            try:
                return self.extract_text_pdfplumber(pdf_content)
            except (ImportError, Exception) as e:
                print(f"pdfplumber failed ({e}), falling back to PyPDF2")
                return self.extract_text_pypdf2(pdf_content)
        elif method == "pypdf2":
            return self.extract_text_pypdf2(pdf_content)
        else:
            raise ValueError(f"Unknown extraction method: {method}")

    def chunk_text(
        self,
        text: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.

        Args:
            text: Full document text
            document_id: Unique document identifier
            metadata: Additional metadata to include with each chunk

        Returns:
            List of chunk dictionaries
        """
        # Split text into chunks
        text_chunks = self.text_splitter.split_text(text)

        # Limit number of chunks (safety)
        if len(text_chunks) > self.max_chunks:
            print(f"Warning: Document has {len(text_chunks)} chunks, "
                  f"limiting to {self.max_chunks}")
            text_chunks = text_chunks[:self.max_chunks]

        # Create chunk objects
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunk_id = f"{document_id}#chunk_{i+1}"

            chunk_metadata = {
                'document_id': document_id,
                'chunk_number': i + 1,
                'total_chunks': len(text_chunks),
                'chunk_text': chunk_text[:500],  # Store preview for quick reference
                'created_at': datetime.now().isoformat(),
                'document_type': 'pdf'
            }

            # Add custom metadata if provided
            if metadata:
                chunk_metadata.update(metadata)

            chunks.append({
                'id': chunk_id,
                'text': chunk_text,  # Full text for embedding
                'metadata': chunk_metadata
            })

        return chunks

    def process_pdf_from_drive(
        self,
        file_id: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        extraction_method: str = "pdfplumber"
    ) -> List[Dict[str, Any]]:
        """
        Complete pipeline: download, extract, chunk.

        Args:
            file_id: Google Drive file ID
            document_id: Unique document identifier
            metadata: Additional metadata for chunks
            extraction_method: PDF extraction method

        Returns:
            List of chunks ready for indexing
        """
        print(f"Downloading PDF from Google Drive (ID: {file_id})...")
        pdf_content = self.download_from_google_drive(file_id)

        print(f"Extracting text using {extraction_method}...")
        text = self.extract_text(pdf_content, method=extraction_method)

        if not text or len(text.strip()) < 100:
            raise Exception("Failed to extract meaningful text from PDF")

        print(f"Extracted {len(text)} characters")

        print("Chunking text...")
        chunks = self.chunk_text(text, document_id, metadata)

        print(f"Created {len(chunks)} chunks")

        return chunks

    def download_from_url(self, url: str) -> bytes:
        """
        Download PDF from any direct URL (Firebase Storage, etc).

        Args:
            url: Direct URL to PDF file

        Returns:
            PDF content as bytes
        """
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise Exception(f"Failed to download PDF from {url}: {e}")

    def process_pdf_from_manifest(
        self,
        material_id: str,
        manifest_path: Path = Config.MANIFEST_PATH
    ) -> List[Dict[str, Any]]:
        """
        Process a PDF using information from manifest.json.

        Args:
            material_id: Material ID from manifest
            manifest_path: Path to manifest.json

        Returns:
            List of chunks ready for indexing
        """
        # Load manifest
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        # Find material
        material = None
        for mat in manifest.get('materials', []):
            if mat['id'] == material_id:
                material = mat
                break

        if not material:
            raise ValueError(f"Material '{material_id}' not found in manifest")

        raw_url = material.get('raw_url', '')

        # Prepare metadata
        metadata = {
            'document_title': material.get('title', ''),
            'document_url': material.get('url', ''),
            'learning_unit': material.get('learning_unit', ''),
            'course': material.get('course', ''),
            'material_type': material.get('type', 'pdf'),
            'total_pages': material.get('pages', 0),
            'notes': material.get('notes', '')
        }

        # Add section information if available
        if 'sections' in material:
            metadata['sections'] = json.dumps(material['sections'])

        # Determine URL type and download accordingly
        if 'firebasestorage.googleapis.com' in raw_url:
            # Firebase Storage URL - download directly
            print(f"Downloading PDF from Firebase Storage...")
            pdf_content = self.download_from_url(raw_url)

            print(f"Extracting text using pdfplumber...")
            text = self.extract_text(pdf_content, method="pdfplumber")

            if not text or len(text.strip()) < 100:
                raise Exception("Failed to extract meaningful text from PDF")

            print(f"Extracted {len(text)} characters")

            print("Chunking text...")
            chunks = self.chunk_text(text, material_id, metadata)

            print(f"Created {len(chunks)} chunks")

            return chunks

        elif 'drive.google.com' in raw_url or 'id=' in raw_url:
            # Google Drive URL - extract file ID
            file_id = raw_url.split('id=')[1].split('&')[0]
            return self.process_pdf_from_drive(
                file_id=file_id,
                document_id=material_id,
                metadata=metadata
            )
        else:
            raise ValueError(f"Unsupported URL type: {raw_url}")


if __name__ == "__main__":
    # Test PDF processor
    processor = PDFProcessor()

    print("PDF Processor initialized")
    print(f"Chunk size: {processor.chunk_size} characters")
    print(f"Chunk overlap: {processor.chunk_overlap} characters")
    print(f"Max chunks per PDF: {processor.max_chunks}")

    # Test with manifest
    try:
        manifest_path = Config.MANIFEST_PATH
        if manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                materials = manifest.get('materials', [])
                if materials:
                    print(f"\nFound {len(materials)} material(s) in manifest:")
                    for mat in materials:
                        print(f"  - {mat['id']}: {mat['title']}")
                else:
                    print("\nNo materials found in manifest")
        else:
            print(f"\nManifest not found at {manifest_path}")
    except Exception as e:
        print(f"Error reading manifest: {e}")
