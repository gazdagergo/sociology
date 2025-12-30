#!/usr/bin/env python3
"""
Search indexed PDFs using semantic search.

Usage:
    python scripts/search_pdfs.py "your search query"
    python scripts/search_pdfs.py "query" --top-k 10
    python scripts/search_pdfs.py "query" --filter document_id=material-001
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pinecone_manager import PineconeManager
from config import Config


def format_result(result: dict, index: int) -> str:
    """
    Format a search result for display.

    Args:
        result: Search result dictionary
        index: Result index (1-based)

    Returns:
        Formatted string
    """
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"Result #{index} (Score: {result['score']:.4f})")
    lines.append(f"{'='*60}")

    metadata = result.get('metadata', {})

    # Document info
    lines.append(f"\nDocument: {metadata.get('document_title', 'Unknown')}")
    lines.append(f"ID: {result['id']}")
    lines.append(f"Type: {metadata.get('material_type', 'pdf')}")

    if 'learning_unit' in metadata:
        lines.append(f"Learning Unit: {metadata['learning_unit']}")

    if 'chunk_number' in metadata:
        lines.append(f"Chunk: {metadata['chunk_number']}/{metadata.get('total_chunks', '?')}")

    # Text preview
    chunk_text = metadata.get('chunk_text', '')
    if chunk_text:
        lines.append(f"\nText Preview:")
        lines.append(f"{chunk_text[:300]}{'...' if len(chunk_text) > 300 else ''}")

    # URL
    if 'document_url' in metadata:
        lines.append(f"\nSource: {metadata['document_url']}")

    return '\n'.join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Semantic search across indexed PDFs"
    )
    parser.add_argument(
        'query',
        help='Search query'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=Config.DEFAULT_TOP_K,
        help=f'Number of results to return (default: {Config.DEFAULT_TOP_K})'
    )
    parser.add_argument(
        '--filter',
        action='append',
        help='Metadata filter (format: key=value). Can be used multiple times.'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=Config.SIMILARITY_THRESHOLD,
        help=f'Minimum similarity score (default: {Config.SIMILARITY_THRESHOLD})'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    if not args.json:
        print("=== PDF Semantic Search ===\n")
        print(f"Query: \"{args.query}\"")
        print(f"Top-K: {args.top_k}")
        print(f"Threshold: {args.threshold}")

    # Parse filters
    filter_metadata = None
    if args.filter:
        filter_metadata = {}
        for f in args.filter:
            if '=' not in f:
                print(f"✗ Invalid filter format: {f}")
                print("Use format: key=value")
                return 1
            key, value = f.split('=', 1)
            filter_metadata[key.strip()] = value.strip()

        if not args.json:
            print(f"Filters: {filter_metadata}")

    # Initialize manager
    try:
        manager = PineconeManager()
        if not args.json:
            print("\n✓ Connected to Pinecone\n")
    except Exception as e:
        print(f"✗ Failed to initialize Pinecone: {e}")
        return 1

    # Search
    try:
        if not args.json:
            print("Searching...")

        results = manager.search(
            query=args.query,
            top_k=args.top_k,
            filter_metadata=filter_metadata,
            include_metadata=True
        )

        # Filter by threshold
        results = [r for r in results if r['score'] >= args.threshold]

        if args.json:
            # JSON output
            print(json.dumps({
                'query': args.query,
                'top_k': args.top_k,
                'threshold': args.threshold,
                'filters': filter_metadata,
                'result_count': len(results),
                'results': results
            }, indent=2))
        else:
            # Human-readable output
            if not results:
                print("\n✗ No results found")
                print(f"\nTry:")
                print(f"  - Lowering the threshold (--threshold {args.threshold - 0.1})")
                print(f"  - Increasing top-k (--top-k {args.top_k * 2})")
                print(f"  - Using different search terms")
                return 1

            print(f"\n✓ Found {len(results)} result(s)\n")

            for i, result in enumerate(results, 1):
                print(format_result(result, i))

            # Summary
            print(f"\n{'='*60}")
            print(f"Showing {len(results)} result(s)")
            if len(results) >= args.top_k:
                print(f"(Limited to top {args.top_k}. Use --top-k to see more)")
            print(f"{'='*60}\n")

        return 0

    except Exception as e:
        print(f"\n✗ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
