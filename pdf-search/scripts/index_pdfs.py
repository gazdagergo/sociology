#!/usr/bin/env python3
"""
Index PDFs from manifest.json into Pinecone.

Usage:
    python scripts/index_pdfs.py                    # Index all PDFs
    python scripts/index_pdfs.py <material_id>      # Index specific PDF
    python scripts/index_pdfs.py --reindex <id>     # Reindex (delete + index)
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pinecone_manager import PineconeManager
from pdf_processor import PDFProcessor
from config import Config


def index_material(
    material_id: str,
    manager: PineconeManager,
    processor: PDFProcessor,
    reindex: bool = False
) -> bool:
    """
    Index a single material from manifest.

    Args:
        material_id: Material ID from manifest
        manager: Pinecone manager instance
        processor: PDF processor instance
        reindex: If True, delete existing chunks first

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n{'='*60}")
        print(f"Processing: {material_id}")
        print(f"{'='*60}\n")

        # Reindex: delete existing chunks first
        if reindex:
            print("Reindexing: Deleting existing chunks...")
            result = manager.delete_by_document_id(material_id)
            if result['success']:
                print(f"✓ {result['message']}")
            else:
                print(f"Warning: {result.get('error', 'Unknown error')}")
            print()

        # Process PDF
        chunks = processor.process_pdf_from_manifest(material_id)

        if not chunks:
            print(f"✗ No chunks created for {material_id}")
            return False

        print(f"\nIndexing {len(chunks)} chunks...")

        # Upsert to Pinecone
        stats = manager.upsert_chunks(chunks, show_progress=True)

        print(f"\n✓ Indexing complete!")
        print(f"  Total chunks: {stats['total']}")
        print(f"  Upserted: {stats['upserted']}")
        print(f"  Failed: {stats['failed']}")

        return stats['failed'] == 0

    except Exception as e:
        print(f"\n✗ Error indexing {material_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Index PDFs from manifest into Pinecone"
    )
    parser.add_argument(
        'material_id',
        nargs='?',
        help='Specific material ID to index (optional, indexes all if not provided)'
    )
    parser.add_argument(
        '--reindex',
        action='store_true',
        help='Delete existing chunks before indexing'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Index all materials in manifest'
    )

    args = parser.parse_args()

    print("=== PDF Indexing Tool ===\n")

    # Validate configuration
    is_valid, error = Config.validate()
    if not is_valid:
        print(f"✗ Configuration error: {error}")
        return 1

    # Load manifest
    try:
        with open(Config.MANIFEST_PATH, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"✗ Failed to load manifest: {e}")
        return 1

    materials = manifest.get('materials', [])
    if not materials:
        print("✗ No materials found in manifest")
        return 1

    # Initialize managers
    try:
        manager = PineconeManager()
        processor = PDFProcessor()
        print("✓ Managers initialized\n")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return 1

    # Determine which materials to index
    if args.material_id:
        # Index specific material
        material_ids = [args.material_id]
    elif args.all or not args.material_id:
        # Index all materials
        material_ids = [mat['id'] for mat in materials]
        print(f"Indexing all {len(material_ids)} materials\n")
    else:
        material_ids = []

    # Validate material IDs
    available_ids = {mat['id'] for mat in materials}
    invalid_ids = [mid for mid in material_ids if mid not in available_ids]
    if invalid_ids:
        print(f"✗ Material(s) not found in manifest: {', '.join(invalid_ids)}")
        print(f"\nAvailable materials:")
        for mat in materials:
            print(f"  - {mat['id']}: {mat['title']}")
        return 1

    # Index materials
    results = {
        'success': [],
        'failed': []
    }

    for material_id in material_ids:
        success = index_material(
            material_id=material_id,
            manager=manager,
            processor=processor,
            reindex=args.reindex
        )

        if success:
            results['success'].append(material_id)
        else:
            results['failed'].append(material_id)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total materials: {len(material_ids)}")
    print(f"Successfully indexed: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")

    if results['failed']:
        print(f"\nFailed materials:")
        for mat_id in results['failed']:
            print(f"  - {mat_id}")

    # Show index stats
    try:
        stats = manager.get_index_stats()
        print(f"\nIndex statistics:")
        print(f"  Total vectors: {stats['total_vector_count']}")
        print(f"  Namespaces: {list(stats.get('namespaces', {}).keys())}")
    except Exception as e:
        print(f"\nCould not retrieve index stats: {e}")

    return 0 if not results['failed'] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
