"""
Example: Using PDF search system programmatically.

This demonstrates how to use the PDF search system in your own code.
"""

from pinecone_manager import PineconeManager
from pdf_processor import PDFProcessor
from config import Config


def example_index_pdf():
    """Example: Index a PDF from manifest."""
    print("=== Indexing PDF ===\n")

    # Initialize
    processor = PDFProcessor()
    manager = PineconeManager()

    # Process PDF from manifest
    material_id = "sozialwissenschaftliches-arbeiten"

    try:
        # Extract and chunk PDF
        chunks = processor.process_pdf_from_manifest(material_id)

        print(f"\nCreated {len(chunks)} chunks")
        print(f"First chunk ID: {chunks[0]['id']}")
        print(f"First chunk preview: {chunks[0]['metadata']['chunk_text'][:100]}...")

        # Index chunks
        stats = manager.upsert_chunks(chunks, show_progress=True)

        print(f"\n✓ Indexed {stats['upserted']} chunks")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_search():
    """Example: Search for content."""
    print("\n=== Searching PDFs ===\n")

    manager = PineconeManager()

    # Search for content
    query = "Wie schreibt man eine wissenschaftliche Arbeit?"

    try:
        results = manager.search(
            query=query,
            top_k=3,
            include_metadata=True
        )

        print(f"Query: '{query}'")
        print(f"Found {len(results)} results\n")

        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result['score']:.4f}")
            print(f"   Document: {result['metadata']['document_title']}")
            print(f"   Chunk: {result['metadata']['chunk_number']}/{result['metadata']['total_chunks']}")
            print(f"   Text: {result['metadata']['chunk_text'][:150]}...")
            print()

    except Exception as e:
        print(f"✗ Error: {e}")


def example_filtered_search():
    """Example: Search with metadata filters."""
    print("\n=== Filtered Search ===\n")

    manager = PineconeManager()

    query = "Literaturrecherche"
    filters = {
        'learning_unit': 'LE_I'
    }

    try:
        results = manager.search(
            query=query,
            top_k=5,
            filter_metadata=filters,
            include_metadata=True
        )

        print(f"Query: '{query}'")
        print(f"Filters: {filters}")
        print(f"Found {len(results)} results\n")

        for result in results:
            print(f"- {result['metadata']['document_title']}")
            print(f"  Learning Unit: {result['metadata']['learning_unit']}")
            print(f"  Score: {result['score']:.4f}")
            print()

    except Exception as e:
        print(f"✗ Error: {e}")


def example_delete_document():
    """Example: Delete a document from index."""
    print("\n=== Deleting Document ===\n")

    manager = PineconeManager()

    document_id = "test-document"  # Replace with actual ID

    try:
        result = manager.delete_by_document_id(document_id)

        if result['success']:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_index_stats():
    """Example: Get index statistics."""
    print("\n=== Index Statistics ===\n")

    manager = PineconeManager()

    try:
        stats = manager.get_index_stats()

        print(f"Index Name: {manager.index_name}")
        print(f"Total Vectors: {stats['total_vector_count']}")
        print(f"Dimension: {stats['dimension']}")
        print(f"Index Fullness: {stats['index_fullness']:.2%}")

        namespaces = stats.get('namespaces', {})
        if namespaces:
            print(f"\nNamespaces:")
            for ns, ns_stats in namespaces.items():
                vector_count = ns_stats.get('vector_count', 0)
                print(f"  {ns}: {vector_count} vectors")

    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run examples."""
    print("=" * 60)
    print("PDF Search System - Usage Examples")
    print("=" * 60)

    # Check configuration
    is_valid, error = Config.validate()
    if not is_valid:
        print(f"\n✗ Configuration error: {error}")
        print("Please set up your .env file first")
        return

    print("\n✓ Configuration valid\n")

    # Uncomment the examples you want to run:

    # example_index_stats()
    # example_search()
    # example_filtered_search()

    # WARNING: These modify data
    # example_index_pdf()
    # example_delete_document()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("Uncomment the examples you want to run in main()")
    print("=" * 60)


if __name__ == "__main__":
    main()
