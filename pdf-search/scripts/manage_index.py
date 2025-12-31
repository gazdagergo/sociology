#!/usr/bin/env python3
"""
Manage Pinecone index: view stats, delete documents, reset index.

Usage:
    python scripts/manage_index.py stats
    python scripts/manage_index.py delete <document_id>
    python scripts/manage_index.py list
    python scripts/manage_index.py reset --confirm
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pinecone_manager import PineconeManager
from config import Config


def show_stats(manager: PineconeManager):
    """Show index statistics."""
    try:
        stats = manager.get_index_stats()

        print("\n=== Index Statistics ===\n")
        print(f"Index Name: {manager.index_name}")
        print(f"Namespace: {manager.namespace}")
        print(f"Total Vectors: {stats['total_vector_count']}")
        print(f"Dimension: {stats['dimension']}")
        print(f"Index Fullness: {stats['index_fullness']:.2%}")

        namespaces = stats.get('namespaces', {})
        if namespaces:
            print(f"\nNamespaces:")
            for ns, ns_stats in namespaces.items():
                print(f"  {ns}: {ns_stats.get('vector_count', 0)} vectors")

        print()
        return 0

    except Exception as e:
        print(f"✗ Failed to get stats: {e}")
        return 1


def list_documents(manager: PineconeManager):
    """List all indexed documents."""
    try:
        # Load manifest to show indexed documents
        with open(Config.MANIFEST_PATH, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        materials = manifest.get('materials', [])

        print("\n=== Indexed Documents ===\n")

        if not materials:
            print("No materials found in manifest")
            return 0

        for mat in materials:
            mat_id = mat['id']
            title = mat['title']
            mat_type = mat.get('type', 'unknown')
            pages = mat.get('pages', '?')

            print(f"ID: {mat_id}")
            print(f"  Title: {title}")
            print(f"  Type: {mat_type}")
            print(f"  Pages: {pages}")
            print()

        print(f"Total: {len(materials)} document(s)")
        print()

        return 0

    except Exception as e:
        print(f"✗ Failed to list documents: {e}")
        return 1


def delete_document(manager: PineconeManager, document_id: str):
    """Delete a document from the index."""
    try:
        print(f"\nDeleting document: {document_id}")

        result = manager.delete_by_document_id(document_id)

        if result['success']:
            print(f"✓ {result['message']}")
            return 0
        else:
            print(f"✗ {result.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        print(f"✗ Failed to delete document: {e}")
        return 1


def reset_index(manager: PineconeManager, confirm: bool):
    """Reset (delete and recreate) the index."""
    if not confirm:
        print("\n⚠️  WARNING: This will delete ALL data in the index!")
        print("To confirm, use: --confirm")
        return 1

    try:
        print("\n⚠️  Deleting index...")
        manager.delete_index(confirm=True)

        print("Creating new index...")
        manager.create_index()

        print("✓ Index reset complete")
        return 0

    except Exception as e:
        print(f"✗ Failed to reset index: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage Pinecone index"
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Stats command
    subparsers.add_parser('stats', help='Show index statistics')

    # List command
    subparsers.add_parser('list', help='List all documents')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a document')
    delete_parser.add_argument('document_id', help='Document ID to delete')

    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset index (delete all data)')
    reset_parser.add_argument('--confirm', action='store_true', help='Confirm reset')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize manager
    try:
        manager = PineconeManager()
    except Exception as e:
        print(f"✗ Failed to initialize Pinecone: {e}")
        return 1

    # Execute command
    if args.command == 'stats':
        return show_stats(manager)
    elif args.command == 'list':
        return list_documents(manager)
    elif args.command == 'delete':
        return delete_document(manager, args.document_id)
    elif args.command == 'reset':
        return reset_index(manager, args.confirm)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
