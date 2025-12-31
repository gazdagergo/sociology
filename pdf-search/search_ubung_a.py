#!/usr/bin/env python3
"""
Search for Policy, Polity, and Politics definitions for Übung A Task 3.
"""

import sys
from pinecone_manager import PineconeManager
from config import Config


def search_term_in_document(manager, term, document_id, page_start, page_end, top_k=5):
    """
    Search for a specific term within a document's page range.

    Args:
        manager: PineconeManager instance
        term: Search term (Policy, Polity, or Politics)
        document_id: Document identifier
        page_start: Starting page number
        page_end: Ending page number
        top_k: Number of results to return

    Returns:
        List of search results
    """
    # Search with document filter
    results = manager.search(
        query=f"{term} Definition Begriffsbestimmung",
        top_k=50,  # Get more results initially
        filter_metadata={'document_id': document_id},
        include_metadata=True
    )

    # Filter by page range manually
    filtered_results = []
    for result in results:
        metadata = result.get('metadata', {})

        # Check if chunk overlaps with our target page range
        chunk_page_start = metadata.get('page_start')
        chunk_page_end = metadata.get('page_end')

        if chunk_page_start is not None and chunk_page_end is not None:
            # Check if there's any overlap with target range
            if not (chunk_page_end < page_start or chunk_page_start > page_end):
                filtered_results.append(result)

        if len(filtered_results) >= top_k:
            break

    return filtered_results


def format_excerpt(term, results, document_title):
    """Format search results as an excerpt."""
    if not results:
        return f"\n## {term}\n\n**Quelle**: {document_title}\n\n❌ Keine Definition gefunden\n"

    output = []
    output.append(f"\n## {term}")
    output.append(f"\n**Quelle**: {document_title}\n")

    for i, result in enumerate(results[:3], 1):  # Show top 3
        metadata = result.get('metadata', {})
        score = result['score']

        # Extract page info
        page_num = metadata.get('page_number', 'N/A')
        pdf_page = metadata.get('pdf_page_number', 'N/A')
        page_range = metadata.get('page_range', 'N/A')

        # Get document URL
        doc_url = metadata.get('document_url', '')

        # Create direct link if we have PDF page number
        direct_link = ""
        if pdf_page != 'N/A' and doc_url:
            direct_link = f"{doc_url}#page={pdf_page}"

        # Format output
        output.append(f"### Fundstelle {i} (Relevanz: {score:.3f})")
        output.append(f"- 📄 **Gedruckte Seite**: {page_num} (Seitenbereich: {page_range})")
        output.append(f"- 🔗 **PDF Seite**: {pdf_page}")
        if direct_link:
            output.append(f"- 🌐 **Direkter Link**: {direct_link}")
        output.append(f"\n**Text**:")
        output.append("```")
        output.append(metadata.get('chunk_text', '').strip())
        output.append("```")
        output.append("")

    return '\n'.join(output)


def main():
    """Main entry point."""
    print("="*80)
    print("ÜBUNG A - TASK 3: Begriffsbestimmungen (Policy, Polity, Politics)")
    print("="*80)

    # Initialize Pinecone
    try:
        print("\nInitializing Pinecone connection...")
        manager = PineconeManager()
        print("✓ Connected to Pinecone\n")
    except Exception as e:
        print(f"✗ Failed to initialize Pinecone: {e}")
        return 1

    # Define search parameters
    searches = [
        {
            'term': 'Policy',
            'document_id': 'politikfeldanalyse-blum-schubert',
            'document_title': 'Politikfeldanalyse. Eine Einführung (Blum & Schubert, 2018)',
            'page_start': 9,
            'page_end': 15
        },
        {
            'term': 'Polity',
            'document_id': 'politikfeldanalyse-blum-schubert',
            'document_title': 'Politikfeldanalyse. Eine Einführung (Blum & Schubert, 2018)',
            'page_start': 9,
            'page_end': 15
        },
        {
            'term': 'Politics',
            'document_id': 'politikfeldanalyse-blum-schubert',
            'document_title': 'Politikfeldanalyse. Eine Einführung (Blum & Schubert, 2018)',
            'page_start': 9,
            'page_end': 15
        },
        {
            'term': 'Policy',
            'document_id': 'lehrbuch-politikfeldanalyse',
            'document_title': 'Lehrbuch der Politikfeldanalyse (Schubert & Bandelow, 2014)',
            'page_start': 1,
            'page_end': 24
        },
        {
            'term': 'Polity',
            'document_id': 'lehrbuch-politikfeldanalyse',
            'document_title': 'Lehrbuch der Politikfeldanalyse (Schubert & Bandelow, 2014)',
            'page_start': 1,
            'page_end': 24
        },
        {
            'term': 'Politics',
            'document_id': 'lehrbuch-politikfeldanalyse',
            'document_title': 'Lehrbuch der Politikfeldanalyse (Schubert & Bandelow, 2014)',
            'page_start': 1,
            'page_end': 24
        }
    ]

    # Perform searches
    all_excerpts = []

    for search in searches:
        print(f"Searching for '{search['term']}' in {search['document_title']}")
        print(f"  Pages: {search['page_start']}-{search['page_end']}")

        results = search_term_in_document(
            manager=manager,
            term=search['term'],
            document_id=search['document_id'],
            page_start=search['page_start'],
            page_end=search['page_end'],
            top_k=3
        )

        print(f"  Found {len(results)} result(s)\n")

        excerpt = format_excerpt(search['term'], results, search['document_title'])
        all_excerpts.append({
            'term': search['term'],
            'document': search['document_title'],
            'excerpt': excerpt
        })

    # Print organized results
    print("\n" + "="*80)
    print("RESULTS: EXZERPTE DER DREI BEGRIFFE")
    print("="*80)

    # Group by term
    for term in ['Policy', 'Polity', 'Politics']:
        print(f"\n{'#'*80}")
        print(f"# {term.upper()}")
        print(f"{'#'*80}")

        for excerpt_data in all_excerpts:
            if excerpt_data['term'] == term:
                print(excerpt_data['excerpt'])

        print("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())